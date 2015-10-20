import nfldb
import pandas as pd
import numpy as np

from ml.feature_extraction.nfldb_feature_extraction import WeeklyPlayerData
from ml.feature_extraction.nfldb_feature_extraction import LagPlayerData
from ml.feature_extraction.nfldb_feature_extraction import MeanPlayerData
from ml.feature_extraction.nfldb_feature_extraction import ExtractColumns
from ml.feature_extraction.nfldb_feature_extraction import HandleNaN
from ml.feature_extraction.nfldb_feature_extraction import FilterPlayedPercent

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion

def train_test_split_index(n,test_size=0.2):
	rand_i = np.random.choice(range(n), n, replace=False)
	test_i = rand_i[range(int(round(n*test_size)))]
	train_i = rand_i[range(int(round(n*test_size)),n)]
	return train_i, test_i

def split_by_year_week(X, test_yr_wk):
	train_i = []
	test_i = []
	for i in range(X.shape[0]):
		match = False
		row_yr_wk = (X.iloc[i]['year'], X.iloc[i]['week'])
		for yr_wk in test_yr_wk:
			if row_yr_wk == yr_wk:
				match = True
				test_i += [i]
				break
		if not match:
			train_i += [i]
	return train_i, test_i


def main():
	# connect to nfldb
	db = nfldb.connect()
	result_path = '../results'

	# make player data transformer
	yr_wk = [(j, i) for j in range(2009,2015) for i in range(1,18)]
	yr_wk += [(2015, i) for i in range(1,5)]

	#stats = ['rushing_yds','rushing_att']
	stats = ['receiving_rec', 'receiving_tar', 'receiving_tds', 'receiving_yac_yds', 'receiving_yds', 'rushing_att', 'rushing_tds','rushing_yds']

	player_info = ['player_id','full_name','position']
	playerData = WeeklyPlayerData(db=db, yr_wk=yr_wk, stats=stats, player_info=player_info, fill_time=True, position='RB')

	# creates lags of the data
	lag_cols = ['year', 'week', 'played'] + stats
	lagData = LagPlayerData(nlag=6, groupby_cols=['player_id'], lag_cols=lag_cols, same_year_bool=True)

	# creates means of the data
	mean_cols = stats
	meanData = MeanPlayerData(groupby_cols=['player_id'], mean_cols=mean_cols)


	# pipeline for getting data
	#pipe = Pipeline(steps=[('data',playerData), ('lag',lagData)])
	pipe1 = Pipeline(steps=[('data',playerData), ('lag',lagData), ('mean',meanData)])
	processed_data = pipe1.fit_transform(X=None)
	# print processed_data


	# pipeline for seting which columns we want and handling NaN
	pct_played_threshold = 0.2
	pipe2_steps = [('handle',HandleNaN(method='fill')), ('filterplayed',FilterPlayedPercent(pct_played_threshold=pct_played_threshold))]
	pipe2 = Pipeline(steps=pipe2_steps)

	all_columns = pipe2.fit_transform(X=processed_data)

	# picks columns to model
	lag_cols = [stat + '_lag' for stat in stats]
	mean_cols = [stat + '_mean' for stat in stats]
	other_cols = ['same_year_lag', 'played_lag']

	infoColumns = ExtractColumns(like=[], exact=['year','week','time','player_id','full_name'])
	row_info = infoColumns.fit_transform(X=all_columns)

	yr_wk_pred = [(2015, 4)]
	train_i, predict_i = split_by_year_week(all_columns, yr_wk_pred)
	df_pred = row_info.iloc[predict_i]

	# set y_col
	y_cols = ['receiving_rec', 'receiving_tds', 'receiving_yds', 'rushing_att', 'rushing_tds','rushing_yds']

	for y_col in y_cols:
		# Pick the right columns
		keep_like = [y_col] + lag_cols + mean_cols + other_cols
		pickColumns = ExtractColumns(like=keep_like)
		X_y = pickColumns.fit_transform(X=all_columns)
		# get X and y
		y = X_y[y_col]
		X = X_y.drop(y_col, axis=1)
		# random split train and test
		train_i, test_i = train_test_split_index(X.shape[0], test_size=0.05)
		# set up data
		y_train = y.iloc[train_i]
		y_test = y.iloc[test_i]
		X_train = X.iloc[train_i]
		X_test = X.iloc[test_i]
		### Test Predictions
		# Gradident Boosting
		gbr = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1).fit(X_train, y_train)
		predict_test = gbr.predict(X_test)
		gbr_rmse = mean_squared_error(y_test, predict_test)**0.5
		gbr_mae = mean_absolute_error(y_test, predict_test)
		# Random Forest Regressor
		rf = RandomForestRegressor().fit(X_train, y_train)
		predict_test = rf.predict(X_test)
		rf_rmse = mean_squared_error(y_test, predict_test)**0.5
		rf_mae = mean_absolute_error(y_test, predict_test)
		# Linear Regression
		lr = LinearRegression().fit(X_train, y_train)
		predict_test = lr.predict(X_test)
		lr_rmse = mean_squared_error(y_test, predict_test)**0.5
		lr_mae = mean_absolute_error(y_test, predict_test)
		# Print Results
		print 'Predictng %s' % (y_col)
		print 'Gradient Boosting: RMSE %.2f yards | MAE %.2f yards' % (gbr_rmse, gbr_mae)
		print 'Random Forest: RMSE %.2f yards | MAE %.2f yards' % (rf_rmse, rf_mae)
		print 'Linear Regression: RMSE %.2f yards | MAE %.2f yards' % (lr_rmse, lr_mae)
		# Build full models on all but the last week & predict the last week
		gbr = gbr.fit(X.iloc[train_i], y.iloc[train_i])
		rf = rf.fit(X.iloc[train_i], y.iloc[train_i])
		lr = lr.fit(X.iloc[train_i], y.iloc[train_i])
		#### Next week's predictions
		#pipe1 = pipe1.set_params(data__yr_wk=yr_wk_pred)
		#data1 = pipe1.transform(X=None)
		#data2 = pipe2.transform(X=data1)
		#X_y_pred = pickColumns.transform(X=data2)
		#info_pred = infoColumns.transform(X=data2)
		#X_pred = X_y_pred.drop(y_col, axis=1)
		#y_pred = X_y_pred[y_col]
		# Make prediction, just gbr for now
		preds = gbr.predict(X.iloc[predict_i])
		df_pred[y_col] = preds
	
	out_path = result_path + '/predictions' + '_' + str(int(yr_wk_pred[0][0])) + '_' + str(int(yr_wk_pred[0][1])) + '.json'
	df_pred.to_json(path_or_buf = out_path, orient = 'records')

if __name__ == "__main__":
	main()


