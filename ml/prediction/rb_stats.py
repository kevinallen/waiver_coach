import nfldb
import pandas as pd
import numpy as np

from ml.feature_extraction.nfldb_feature_extraction import ExtractColumns
from ml.feature_extraction.nfldb_feature_extraction import load_feature_set
from ml.feature_extraction.nfldb_feature_extraction import prediction_feature_set

from ml.helpers.scoring_helpers import make_scorer
from ml.helpers.scoring_helpers import score_stats
from ml.helpers.testing_helpers import train_test_split_index
from ml.helpers.testing_helpers import split_by_year_week

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

def main():
	db = nfldb.connect()
	result_path='../results'
	full_train, pipe, stats = load_feature_set(db)

	# picks columns to model
	lag_cols = [stat + '_lag' for stat in stats]
	mean_cols = [stat + '_mean' for stat in stats]
	other_cols = ['same_year_lag', 'played_lag']

	infoColumns = ExtractColumns(like=[], exact=['year','week','time','player_id','full_name'])
	row_info = infoColumns.fit_transform(X=full_train)

	pred_data, predict_i, pred_info, pred_yr_wk = prediction_feature_set(db, pipe, infoColumns)

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

	    ### Test Predictions
	    
	    predict_proba = y_col == 'played'
	    
	    if(predict_proba):
	        models = {
	            'gb':GradientBoostingClassifier(n_estimators=100, learning_rate=0.1),
	            'rf':RandomForestClassifier(),
	            'lin':LogisticRegression()
	        }
	    else:
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

	    # Print Results
	    print 'Predicting %s' % (y_col)
	    print 'Gradient Boosting: RMSE %.2f | MAE %.2f' % (gb_scores['rmse'], gb_scores['mae'])
	    print 'Random Forest: RMSE %.2f | MAE %.2f' % (rf_scores['rmse'], rf_scores['mae'])
	    print '%s Regression: RMSE %.2f | MAE %.2f' % ('Logistic' if predict_proba else 'Linear', lin_scores['rmse'], lin_scores['mae'])
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

	    pred_results.loc[:,y_col] = preds

	out_path = result_path + '/predictions' + '_' + str(int(pred_yr_wk[0])) + '_' + str(int(pred_yr_wk[1])) + '.json'
	pred_results.to_json(path_or_buf = out_path, orient = 'records')

if __name__ == "__main__":
	main()


