import argparse
from pymongo import MongoClient
import pandas as pd
import nfldb
import scipy as sp

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error

from ml.feature_extraction.nfldb_feature_extraction import WeeklyPlayerData
from ml.feature_extraction.nfldb_feature_extraction import AddNameKey
from ml.feature_extraction.nfldb_feature_extraction import HandleNaN
from ml.mongo_helpers.web_helpers import ProjectedPlayerData
from ml.helpers.testing_helpers import train_test_split_index

def main(y_col, predict_week):
    # get historical data
    db = nfldb.connect()

    yr_wk = [(2015, i) for i in range(1,predict_week)]
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
    pipe = Pipeline(steps=[('data', data), ('nan',HandleNaN())])
    proj_data = pipe.fit_transform(X=None)

    # get stats for next week then remove player info
    next_week_proj = proj_data.loc[proj_data.week == predict_week]
    info_cols = ['name','name_key','team','week','year','position']
    pred_info = next_week_proj[info_cols]
    next_week_proj.drop(info_cols, axis=1, inplace=True)

    # join the two dataframes
    df = pd.merge(proj_data, hist_data, how="inner", on=["name_key","week","year"])
    # drop the week you want to predict from the training data
    df = df[df.week < predict_week]

    # store the player data and then remove those columns from the training data
    info_cols = ['name','name_key','position_x','position_y','team','week','year',
                 'full_name','played','player_id']
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

    regr = LinearRegression()
    regr.fit(X_train, y_train)
    pred = regr.predict(X_test)
    print 'Predicting ', y_col
    print 'Actual statistics:'
    print y_test.describe()
    print
    print 'Projected statistics:'
    print sp.stats.describe(pred)
    print
    print "RMSE: ", mean_squared_error(y_test, pred)**0.5
    print "MAE: ", mean_absolute_error(y_test, pred)
    print "intercept: ", regr.intercept_
    print "coefficients:"
    for col, coef in zip(X_train.columns, regr.coef_):
        print "   ", col, coef
    print

    pred_labels = []
    for player in pred_info.iterrows():
        pred_labels.append((player[1]['name'], player[1]['week']))

    pred = regr.predict(next_week_proj)

    # print out predicted data for inspection
    print 'Player\tWeek\tRushing yards'
    for (player,week), prediction in zip(pred_labels,pred):
        print "\t".join([player,str(week),str(prediction)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("y_column", help="column to predict")
    parser.add_argument("week", type=int, help="predict y_column for this week")
    args = parser.parse_args()
    main(y_col = args.y_column, predict_week=args.week)
