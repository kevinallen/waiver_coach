import argparse
import nfldb
import pandas as pd
import numpy as np
from pymongo import MongoClient

from ml.feature_extraction.nfldb_feature_extraction import ExtractColumns
from ml.feature_extraction.nfldb_feature_extraction import load_feature_set
from ml.feature_extraction.nfldb_feature_extraction import prediction_feature_set
from ml.feature_extraction.nfldb_feature_extraction import WeeklyPlayerData
from ml.feature_extraction.nfldb_feature_extraction import AddNameKey
from ml.feature_extraction.nfldb_feature_extraction import HandleNaN

from ml.helpers.scoring_helpers import make_scorer
from ml.helpers.scoring_helpers import score_stats
from ml.helpers.testing_helpers import train_test_split_index
from ml.helpers.testing_helpers import split_by_year_week
from ml.helpers.nfldb_helpers import player_team_info
from ml.mongo_helpers.web_helpers import VegasData
from ml.mongo_helpers.web_helpers import ProjectedPlayerData

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KernelDensity
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.cross_validation import cross_val_predict

from sklearn.dummy import DummyRegressor
from sklearn.dummy import DummyClassifier

def result_row(method, results, stat, learner='', rows=[]):
    row = {'stat':stat, 'method':method, 'learner':learner, 'rmse':results['rmse'], 'mae':results['mae']}
    rows.append(row)


def fit_predict(model, X_train, y_train, X_test = None, y_test = None, predict_proba = False):
    model = model.fit(X_train, y_train)
    return_obj = (model,)
    if X_test is not None:
        if predict_proba:
            pred_test = model.predict_proba(X_test)[:,1]
        else:
            pred_test = model.predict(X_test)

        return_obj += (pred_test,)

        if y_test is not None:
            rmse = mean_squared_error(y_test, pred_test)**0.5
            mae = mean_absolute_error(y_test, pred_test)

            return_obj += ({'rmse':rmse, 'mae':mae},)

    return(return_obj)

def build_vegas_dataframe(X, y, row_info, model, db, y_col):
    # get vegas data
    client = MongoClient()
    mdb = client.data
    vegas = VegasData(mdb)
    vegas_pipe = Pipeline(steps=[('vegas', vegas)])
    vegas_data = vegas_pipe.fit_transform(X=None)

    # create a new training set with predicted values and vegas data
    cols = ['full_name','player_id','week','year']
    X_with_info = row_info[cols]

    # get model output
    #lr = LinearRegression()
    #predicted = cross_val_predict(lr, X, y)
    predicted = model.predict(X)
    X_with_info.loc[:,y_col] = predicted


    team_info = player_team_info(db)
    with_team = pd.merge(X_with_info, team_info, how='inner', on=['player_id','year','week'])
    with_vegas = pd.merge(with_team, vegas_data, how='left',
        left_on=['team','week','year'],
        right_on=['Favorite_Abbr','Week','Year'])
    X_vegas = pd.merge(with_vegas, vegas_data, how='left',
        left_on=['team','week','year'],
        right_on=['Underdog_Abbr','Week','Year'])

    # TODO: dummy code weekday, month
    # TODO: discuss whether looking at home team here makes sense

    # combine columns with NaN values, caused by left joins above
    cols_to_fill = ['Favorite_Abbr','Underdog_Abbr','Spread','Total']
    for col in cols_to_fill:
        X_vegas.loc[:,col] = X_vegas[col+'_x'].fillna(X_vegas[col+'_y'])

    # determine if player's team is favored
    X_vegas.loc[:,'is_favorite'] = X_vegas['team'] == X_vegas['Favorite_Abbr']
    # want look at interaction of spread and favorite because
    # otherwise spread is ambiguous, mapping False to -1 so sign of spread
    # is reversed
    X_vegas.loc[:,'is_favorite'] = X_vegas['is_favorite'].map({True:1, False:-1})
    X_vegas.loc[:,'spread_x_favorite'] = X_vegas['is_favorite']*X_vegas['Spread']

    # get rid of unnecessary columns
    cols_to_keep = ['full_name','player_id','week','year','team','Total',
        'is_favorite','spread_x_favorite', y_col]
    cols_to_drop = [col for col in X_vegas.columns if col not in cols_to_keep]
    cols_to_drop.extend(['Favorite_Abbr','Underdog_Abbr','Spread'])
    X_vegas.drop(cols_to_drop, axis=1, inplace=True)

    return X_vegas

# TODO pass in nfldb and mongodb as arguments to simplify changes
# TODO make this code year independent
def add_expert_projections(pred_results, pred_week, y_col, info_2015):
    db = nfldb.connect()

    yr_wk = [(2015, i) for i in range(1,pred_week + 1)]
    stats = ['receiving_rec', 'receiving_tar', 'receiving_tds', 'receiving_yac_yds',
             'receiving_yds', 'rushing_att', 'rushing_tds','rushing_yds']
    player_info = ['player_id','full_name','position']
    position = 'RB'

    playerdata = WeeklyPlayerData(db=db, yr_wk=yr_wk, stats=stats,
                                  player_info=player_info, fill_time=True,
                                  position=position)

    pipe = Pipeline(steps=[('data',playerdata), ('key',AddNameKey()),
                           ('nan',HandleNaN(method='fill'))])
    hist_data = pipe.fit_transform(X=None)

    client = MongoClient()
    mdb = client.data

    include_stats = ['fumbles','receptions','rec_yds','rec_tds',
                     'rush_attempts','rush_yds','rush_tds']

    data = ProjectedPlayerData(db=mdb, stats=include_stats, position='RB')
    # data already has name_key, so don't need to add it to pipeline
    pipe = Pipeline(steps=[('data', data), ('nan',HandleNaN())])
    proj_data = pipe.fit_transform(X=None)

    # join the two datasets
    df = pd.merge(proj_data, hist_data, how="inner", on=["name_key","week","year"])

    # drop the week you want to predict from the training data
    df = df[df.week < pred_week]

    # store the player data and then remove those columns from the training data
    info_cols = ['name','name_key','position_x','position_y','team','week',
        'year','full_name','played','player_id']
    hist_info = df[info_cols]
    df.drop(info_cols, axis=1, inplace=True)

    hist_cols = ['rushing_tds','rushing_att','receiving_yds','receiving_yac_yds',
                 'receiving_tds','receiving_tar','receiving_rec','rushing_yds']

    y = df[y_col]
    X = df.drop(hist_cols, axis=1)


    train, test = train_test_split_index(df.shape[0], test_size=0.1, seed=0)

    X_train = X.iloc[train]
    y_train = y.iloc[train]
    X_test = X.iloc[test]
    y_test = y.iloc[test]

    models = {
        'gb':GradientBoostingRegressor(n_estimators=100, learning_rate=0.1),
        'rf':RandomForestRegressor(),
        'lin':LinearRegression()
    }

    gb, gb_test, gb_scores = fit_predict(
        model=models['gb'],
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test)

    rf, rf_test, rf_scores = fit_predict(
        model=models['rf'],
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test)

    lin, lin_test, lin_scores = fit_predict(
        model=models['lin'],
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test)

    print "-"*50
    print "Expert prediction: ", y_col
    print 'Gradient Boosting: RMSE %.2f | MAE %.2f' % (gb_scores['rmse'], gb_scores['mae'])
    print 'Random Forest: RMSE %.2f | MAE %.2f' % (rf_scores['rmse'], rf_scores['mae'])
    print '%s Regression: RMSE %.2f | MAE %.2f' % ('Linear', lin_scores['rmse'], lin_scores['mae'])

    # get stats for the prediction week then remove player info
    next_week_proj = proj_data[proj_data.week == pred_week]
    info_cols = ['name','name_key','team','position','year','week']
    pred_info = next_week_proj[info_cols]
    next_week_proj.drop(info_cols, axis=1, inplace=True)

    # make prediction for next week
    gb.fit(X, y)
    pred = gb.predict(next_week_proj)

    df = pd.DataFrame(pred_info['name_key'])
    df.columns = ['name_key']
    df.loc[:,'expert_' + y_col] = pred

    # before adding name_key, need to add position
    pred_results.loc[:,'position'] = 'RB'

    for column in next_week_proj.columns:
        if column not in pred_results.columns:
            df.loc[:,column] = next_week_proj[column]

    # add name_key (to join on) to data predicted from historical data
    pipe = Pipeline(steps=[('key',AddNameKey())])
    results_with_key = pipe.fit_transform(X=pred_results)
    results_with_expert = pd.merge(results_with_key, df, how="left", on="name_key")

    # make a combined prediction
    pred_with_y = pipe.fit_transform(X=info_2015)
    df_all = pd.merge(proj_data, pred_with_y, how="inner", on=["name_key","week","year"])
    next_week_proj = df_all[df_all.week == pred_week]
    df = df_all[df_all.week < pred_week]

    y = df[y_col]
    info_cols = ['name', 'name_key', 'position_x', 'position_y', 'team', 'week', 'year', 'full_name']
    X = df.drop(info_cols + [y_col], axis=1)

    train, test = train_test_split_index(df.shape[0], test_size=0.1, seed=0)

    X_train = X.iloc[train]
    y_train = y.iloc[train]
    X_test = X.iloc[test]
    y_test = y.iloc[test]

    gb, gb_test, gb_scores = fit_predict(
        model=models['gb'],
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test)

    rf, rf_test, rf_scores = fit_predict(
        model=models['rf'],
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test)

    lin, lin_test, lin_scores = fit_predict(
        model=models['lin'],
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test)

    print "-"*50
    print "Historical expert-adjusted prediction:", y_col
    print 'Gradient Boosting: RMSE %.2f | MAE %.2f' % (gb_scores['rmse'], gb_scores['mae'])
    print 'Random Forest: RMSE %.2f | MAE %.2f' % (rf_scores['rmse'], rf_scores['mae'])
    print '%s Regression: RMSE %.2f | MAE %.2f' % ('Linear', lin_scores['rmse'], lin_scores['mae'])
    print
    print

    pred_info = next_week_proj[info_cols]
    next_week_proj.drop(info_cols + [y_col], axis=1, inplace=True)

    # make prediction for next week
    gb.fit(X, y)
    pred = gb.predict(next_week_proj)

    df = pd.DataFrame(pred_info['name_key'])
    df.columns = ['name_key']
    df.loc[:,'hist_expert_' + y_col] = pred

    # # before adding name_key, need to add position
    # pred_results.loc[:,'position'] = 'RB'

    for column in next_week_proj.columns:
        if column not in results_with_expert.columns:
            df.loc[:,column] = next_week_proj[column]

    results_with_expert_2 = pd.merge(results_with_expert, df, how="left", on="name_key")
    return results_with_expert_2

def main(pred_week, vegas_adjustment=False, run_query=False, expert_projections=False):

    db = nfldb.connect()
    result_path='../results'

    full_train, pipe, stats = load_feature_set(db, load_cached=not run_query, to_yr_wk=(2015, pred_week))

    # picks columns to model
    lag_cols = [stat + '_lag' for stat in stats]
    mean_cols = [stat + '_mean' for stat in stats]
    other_cols = ['same_year_lag', 'played_lag']

    infoColumns = ExtractColumns(like=[], exact=['year','week','time','player_id','full_name'])
    row_info = infoColumns.fit_transform(X=full_train)

    pred_data, predict_i, pred_info, pred_yr_wk = prediction_feature_set(db, pipe, infoColumns, pred_week=pred_week)

    X_all = full_train
    pred_all = pred_data.iloc[predict_i]
    pred_results = pred_info.iloc[predict_i]

    # which rows did players play
    played_bool = full_train['played'] == 1
    played_index = [i for i in range(X_all.shape[0]) if played_bool[i]]

    # random split train and test
    train_index, test_index = train_test_split_index(X_all.shape[0], test_size=0.1, seed=0)

    feature_cols = lag_cols + mean_cols + other_cols
    XColumns = ExtractColumns(like=feature_cols)
    X = XColumns.fit_transform(X=X_all)
    X_pred = XColumns.fit_transform(X=pred_all)

    played_only = True

    y_cols = ['played', 'receiving_rec', 'receiving_tds', 'receiving_yds', 'rushing_att', 'rushing_tds','rushing_yds']

    # added for saving test results for model evaluation
    rows = []

    for y_col in y_cols:

        y = X_all[y_col]

        if(played_only and y_col != 'played'):
            train_i = list(set.intersection(set(train_index), set(played_index)))
            test_i = list(set.intersection(set(test_index), set(played_index)))
        else:
            train_i = train_index
            test_i = test_index

        X_train = X.iloc[train_i]
        y_train = y.iloc[train_i]
        X_test = X.iloc[test_i]
        y_test = y.iloc[test_i]

        # get player info for train and test data
        X_train_info = row_info.iloc[train_i]
        X_test_info = row_info.iloc[test_i]

        ### Test Predictions

        predict_proba = y_col == 'played'

        if(predict_proba):
            models = {
                'gb':GradientBoostingClassifier(n_estimators=100, learning_rate=0.1),
                'rf':RandomForestClassifier(),
                'lin':LogisticRegression(),
                'dum':DummyClassifier()
            }
        else:
            models = {
                'gb':GradientBoostingRegressor(n_estimators=100, learning_rate=0.1),
                'rf':RandomForestRegressor(),
                'lin':LinearRegression(),
                'dum':DummyRegressor()
            }

        gb, gb_test, gb_scores = fit_predict(
            model=models['gb'],
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            predict_proba=predict_proba)

        rf, rf_test, rf_scores = fit_predict(
            model=models['rf'],
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            predict_proba=predict_proba)

        lin, lin_test, lin_scores = fit_predict(
            model=models['lin'],
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            predict_proba=predict_proba)


        dum, dum_test, dum_scores = fit_predict(
            model=models['dum'],
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            predict_proba=predict_proba)

        if vegas_adjustment and y_col != 'played':
            print '-'*50
            print 'Vegas Adjusted:', y_col

            X_train_all = build_vegas_dataframe(X=X_train, y=y_train,
                row_info=X_train_info, model=gb, db=db, y_col=y_col)
            X_test_all = build_vegas_dataframe(X=X_test, y=y_test,
                row_info=X_test_info, model=gb, db=db, y_col=y_col)

            features = [y_col, 'Total','is_favorite','spread_x_favorite']
            X_cols = ExtractColumns(exact=features)
            X_train = X_cols.fit_transform(X=X_train_all)
            X_test = X_cols.fit_transform(X=X_test_all)

            gb_a, gb_test_a, gb_scores_a = fit_predict(
                model=models['gb'],
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test)

            rf_a, rf_test_a, rf_scores_a = fit_predict(
                model=models['rf'],
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test)

            lin_a, lin_test_a, lin_scores_a = fit_predict(
                model=models['lin'],
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test)

            print 'Predicting %s' % (y_col)
            print lin_a.coef_
            print 'Gradient Boosting: RMSE %.2f | MAE %.2f' % (gb_scores_a['rmse'], gb_scores_a['mae'])
            print 'Random Forest: RMSE %.2f | MAE %.2f' % (rf_scores_a['rmse'], rf_scores_a['mae'])
            print '%s Regression: RMSE %.2f | MAE %.2f' % ('Linear', lin_scores_a['rmse'], lin_scores_a['mae'])

        print '-'*50
        print 'Historical Prediction:', y_col
        # Print Results
        print 'Gradient Boosting: RMSE %.2f | MAE %.2f' % (gb_scores['rmse'], gb_scores['mae'])
        print 'Random Forest: RMSE %.2f | MAE %.2f' % (rf_scores['rmse'], rf_scores['mae'])
        print '%s Regression: RMSE %.2f | MAE %.2f' % ('Logistic' if predict_proba else 'Linear', lin_scores['rmse'], lin_scores['mae'])
        print 'Baseline: RMSE %.2f | MAE %.2f' % (dum_scores['rmse'], dum_scores['mae'])
        

        result_row(method='Historical Only', results=gb_scores, stat=y_col, learner='Gradient Boosting', rows=rows)
        result_row(method='Historical Only', results=rf_scores, stat=y_col, learner='Random Forest', rows=rows)
        result_row(method='Historical Only', results=lin_scores, stat=y_col, learner='Logistic' if predict_proba else 'Linear', rows=rows)
        
        result_row(method='Baseline', results=dum_scores, stat=y_col, learner='Stratified' if predict_proba else 'Mean', rows=rows)
        
        result_row(method='Vegas Adjusted', results=gb_scores_a, stat=y_col, learner='Gradient Boosting', rows=rows)
        result_row(method='Vegas Adjusted', results=rf_scores_a, stat=y_col, learner='Random Forest', rows=rows)
        result_row(method='Vegas Adjusted', results=lin_scores_a, stat=y_col, learner='Logistic' if predict_proba else 'Linear', rows=rows)
        

        # Build full models on all data
        gb = gb.fit(X, y)
        rf = rf.fit(X, y)
        lin = lin.fit(X, y)
        #### Next week's predictions
        # Make prediction, just gbr for now

        if(y_col == 'played'):
            preds = gb.predict_proba(X_pred)[:,1]
        else:
            preds = gb.predict(X_pred)
            if expert_projections:
                # create dataframe with predictions for all weeks of current
                # year to use with the expert prediction
                mask = (row_info.year == 2015) & (row_info.week <= pred_week)
                X_2015 = X[mask]
                y_2015 = X_all[mask][y_col]
                preds_2015 = cross_val_predict(gb, X_2015, y_2015)
                info_2015 = row_info[mask][['full_name','week','year']]
                info_2015.loc[:, y_col] = preds_2015
                info_2015.loc[:,'position'] = 'RB'
                info_2015.loc[:, y_col] = X_all[mask][y_col]

        # add our prediction based on historical data to output
        pred_results.loc[:,y_col] = preds

        # add expert projections, then make a final prediction
        if expert_projections and y_col != 'played':
            pred_results = add_expert_projections(pred_results, pred_week, y_col, info_2015)

    pred_results.replace(0, np.nan, inplace=True)
    out_path = result_path + '/predictions' + '_' + str(int(pred_yr_wk[0])) + '_' + str(int(pred_yr_wk[1])) + '.json'
    pred_results.to_json(path_or_buf = out_path, orient = 'records')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vegas_adjustment",
        help="adjust model output using Vegas data", action="store_true")
    parser.add_argument("-q", "--run_query",
        help="query nfldb instead of using cached data", action="store_true")
    parser.add_argument("-x", "--expert_projections",
        help="add expert projections to output", action="store_true")
    parser.add_argument("week", type=int, help="week of 2015 season to predict stats for")
    args = parser.parse_args()
    main(pred_week=args.week, vegas_adjustment=args.vegas_adjustment,
        run_query=args.run_query, expert_projections=args.expert_projections)
