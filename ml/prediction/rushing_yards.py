import nfldb
import pandas as pd
import numpy as np

from ml.feature_extraction.nfldb_feature_extraction import WeeklyPlayerData
from ml.feature_extraction.nfldb_feature_extraction import LagPlayerData
from ml.feature_extraction.nfldb_feature_extraction import ExtractColumns
from ml.feature_extraction.nfldb_feature_extraction import DropNaN

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

def main():
	# connect to nfldb
	db = nfldb.connect()

	# make player data transformer
	yr_wk = [(j, i) for j in [2009,2010,2011,2012,2013,2014] for i in range(1,18)]
	stats = ['rushing_yds','rushing_att']
	player_info = ['player_id','full_name','position']
	playerData = WeeklyPlayerData(db=db, yr_wk=yr_wk, stats=stats, player_info=player_info, position='RB')

	# creates lags of the data
	lag_cols = ['year', 'week', 'rushing_att', 'rushing_yds']
	lagData = LagPlayerData(nlag=8, groupby_cols=['player_id'], lag_cols=lag_cols, same_year_bool=True)

	# picks columns
	keep_like = ['rushing_yds','rushing_yds_lag','rushing_att_lag','same_year_lag']
	pickColumns = ExtractColumns(like=keep_like)

	# pipeline for getting data
	pipe = Pipeline(steps=[('data',playerData), ('lag',lagData), ('keep',pickColumns), ('drop',DropNaN())])
	data = pipe.fit_transform(X=None)


	# get data
	y_col = 'rushing_yds'
	y = data[y_col]
	X = data.drop(y_col, axis=1)

	# split train and test
	train_i, test_i = train_test_split_index(X.shape[0], test_size=0.2)

	y_train = y.iloc[train_i]
	y_test = y.iloc[test_i]
	X_train = X.iloc[train_i]
	X_test = X.iloc[test_i]

	# Gradident Boosting
	gbr = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1).fit(X_train, y_train)
	predict_test = gbr.predict(X_test)

	gbr_mse = mean_squared_error(y_test, predict_test)**0.5
	gbr_mae = mean_absolute_error(y_test, predict_test)

	# Random Forest Regressor
	rf = RandomForestRegressor().fit(X_train, y_train)
	predict_test = rf.predict(X_test)

	rf_mse = mean_squared_error(y_test, predict_test)**0.5
	rf_mae = mean_absolute_error(y_test, predict_test)

	# Linear Regression
	lr = LinearRegression().fit(X_train, y_train)
	predict_test = lr.predict(X_test)

	lr_mse = mean_squared_error(y_test, predict_test)**0.5
	lr_mae = mean_absolute_error(y_test, predict_test)

	print 'Gradient Boosting: MSE %.2f yards | MAE %.2f yards' % (gbr_mse, gbr_mae)
	print 'Random Forest: MSE %.2f yards | MAE %.2f yards' % (rf_mse, rf_mae)
	print 'Linear Regression: MSE %.2f yards | MAE %.2f yards' % (lr_mse, lr_mae)


if __name__ == "__main__":
	main()


