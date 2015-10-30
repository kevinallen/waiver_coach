import nfldb
import pandas as pd
import numpy as np
import pickle

from ml.feature_extraction.nfldb_feature_extraction import WeeklyPlayerData
from ml.feature_extraction.nfldb_feature_extraction import LagPlayerData
from ml.feature_extraction.nfldb_feature_extraction import MeanPlayerData
from ml.feature_extraction.nfldb_feature_extraction import ExtractColumns
from ml.feature_extraction.nfldb_feature_extraction import HandleNaN
from ml.feature_extraction.nfldb_feature_extraction import FilterPlayedPercent
from ml.nfldb_helpers.generic_helpers import week_player_id_list
from ml.nfldb_helpers.generic_helpers import player_current_game_info

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion

def train_test_split_index(n,test_size=0.2,seed=None):
	if(seed):
		np.random.seed(seed)
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
			if row_yr_wk[0] == yr_wk[0] and row_yr_wk[1] == yr_wk[1]:
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
	cache_path = '../data'
	position = 'RB'
	load_cached = True

	if(not load_cached):
		# make player data transformer
		yr_wk = [(j, i) for j in range(2009,2015) for i in range(1,18)]
		yr_wk += [(2015, i) for i in range(1,7)]

		#stats = ['rushing_yds','rushing_att']
		stats = ['receiving_rec', 'receiving_tar', 'receiving_tds', 'receiving_yac_yds', 'receiving_yds', 'rushing_att', 'rushing_tds','rushing_yds']

		player_info = ['player_id','full_name','position']
		playerData = WeeklyPlayerData(db=db, yr_wk=yr_wk, stats=stats, player_info=player_info, fill_time=True, position=position)

		# creates lags of the data
		lag_cols = ['year', 'week', 'played'] + stats
		nlag = 6
		lagData = LagPlayerData(nlag=nlag, groupby_cols=['player_id'], lag_cols=lag_cols, same_year_bool=True)

		# creates means of the data
		mean_cols = stats
		meanData = MeanPlayerData(groupby_cols=['player_id'], mean_cols=mean_cols)

		# pipeline for getting data
		pipe1 = Pipeline(steps=[('data',playerData), ('lag',lagData), ('mean',meanData)])
		#processed_data = pipe1.fit_transform(X=None)

		# print processed_data
		# pipeline for seting which columns we want and handling NaN
		pct_played_threshold = 0.0
		pipe2_steps = [('handle',HandleNaN(method='fill')), ('filterplayed',FilterPlayedPercent(pct_played_threshold=pct_played_threshold))]
		pipe2 = Pipeline(steps=pipe2_steps)

		pipe = Pipeline([('pipe1',pipe1),('pipe2',pipe2)])

		all_columns = pipe.fit_transform(X=None)
		all_columns.position = all_columns.position.astype(str)

		# pickle files
		pickle.dump(pipe.set_params(pipe1__data__db=None), open(cache_path + '/pipe_'+position+'.p', 'wb'))
		pickle.dump(all_columns, open(cache_path + '/data_'+position+'.p', 'wb'))
	else:
		# Load from "cached" (pickled) transformer and data
		# data
		all_columns = pickle.load(open(cache_path + '/data_'+position+'.p', 'rb'))
		# pipeline
		pipe = pickle.load(open(cache_path + '/pipe_'+position+'.p', 'rb'))
		# retrieve the list of stats that was predicted
		pipe_params = pipe.get_params()
		stats = pipe_params['pipe1__data__stats']


	pipe.set_params(pipe1__data__db=db)

	full_train = all_columns

	# picks columns to model
	lag_cols = [stat + '_lag' for stat in stats]
	mean_cols = [stat + '_mean' for stat in stats]
	other_cols = ['same_year_lag', 'played_lag']

	infoColumns = ExtractColumns(like=[], exact=['year','week','time','player_id','full_name'])
	row_info = infoColumns.fit_transform(X=full_train)

	### prediction data
	# prediction pipeline
	pred_data_pipe = pipe#Pipeline(steps=[('pipe1',pipe1),('pipe2',pipe2)])

	# get information we need to make predictions
	season_phase, cur_year, cur_week = nfldb.current(db)
	pred_week = cur_week + 1	
	pred_yr_wk = [(j, i) for j in range(2009,cur_year-1) for i in range(1,18)]
	pred_yr_wk += [(cur_year, i) for i in range(1,pred_week+1)]

	pred_data_pipe.set_params(pipe1__data__yr_wk = pred_yr_wk)

	player_ids = week_player_id_list(db, cur_year, pred_week, position='RB')
	#player_ids = player_ids[0:2] + player_ids[-3:-1]

	pred_data = pred_data_pipe.fit_transform(player_ids)
	pred_info = infoColumns.fit_transform(X=pred_data)

	# get extra info like team and opponent
	# should probably be put in to infoColumns transformer later
	extra_info = player_current_game_info(db, year=cur_year, week=pred_week, player_ids = list(pred_info['player_id']))
	join_on = ['player_id']
	add_on = ['team', 'opp_team', 'at_home']
	pred_info = pred_info.join(extra_info.set_index(join_on).loc[:,add_on], on=join_on)

	# predict for the last week
	pred_yr_wk_t = [pred_yr_wk[-1]]
	garbage_i, predict_i = split_by_year_week(pred_data, pred_yr_wk_t)
	df_pred = pred_info.iloc[predict_i]

	# set y_col
	y_cols = ['played', 'receiving_rec', 'receiving_tds', 'receiving_yds', 'rushing_att', 'rushing_tds','rushing_yds']
	#y_cols = ['rushing_yds', 'played']

	played_only = True

	for y_col in y_cols:
		# Pick the right columns
		keep_like = [y_col] + lag_cols + mean_cols + other_cols
		pickColumns = ExtractColumns(like=keep_like)
		X_y = pickColumns.fit_transform(X=full_train)

		if(played_only and y_col != 'played' and 'played' in X_y.columns):
			played_bool = X_y['played'] == 1
			X_y = X_y[played_bool]

		# get X and y
		y = X_y[y_col]
		X = X_y.drop(y_col, axis=1)

		# random split train and test
		train_i, test_i = train_test_split_index(X.shape[0], test_size=0.1, seed=0)
		# set up data
		y_train = y.iloc[train_i]
		y_test = y.iloc[test_i]
		X_train = X.iloc[train_i]
		X_test = X.iloc[test_i]
		### Test Predictions
		# Gradident Boosting
		gb = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1).fit(X_train, y_train)
		predict_test = gb.predict(X_test)
		gb_rmse = mean_squared_error(y_test, predict_test)**0.5
		gb_mae = mean_absolute_error(y_test, predict_test)
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
		print 'Predicting %s' % (y_col)
		print 'Gradient Boosting: RMSE %.2f | MAE %.2f' % (gb_rmse, gb_mae)
		print 'Random Forest: RMSE %.2f | MAE %.2f' % (rf_rmse, rf_mae)
		print 'Linear Regression: RMSE %.2f | MAE %.2f' % (lr_rmse, lr_mae)
		# Build full models on all data

		gb = gb.fit(X, y)
		rf = rf.fit(X, y)
		lr = lr.fit(X, y)
		#### Next week's predictions
		#pipe1 = pipe1.set_params(data__yr_wk=yr_wk_pred)
		#data1 = pipe1.transform(X=None)
		#data2 = pipe2.transform(X=data1)
		#X_y_pred = pickColumns.transform(X=data2)
		#info_pred = infoColumns.transform(X=data2)
		#X_pred = X_y_pred.drop(y_col, axis=1)
		#y_pred = X_y_pred[y_col]
		# Make prediction, just gbr for now
		X_pred = pickColumns.fit_transform(X=pred_data).drop(y_col, axis=1)
		preds = gb.predict(X_pred.iloc[predict_i])
		df_pred[y_col] = preds

	out_path = result_path + '/predictions' + '_' + str(int(pred_yr_wk_t[0][0])) + '_' + str(int(pred_yr_wk_t[0][1])) + '.json'
	df_pred.to_json(path_or_buf = out_path, orient = 'records')

if __name__ == "__main__":
	main()


