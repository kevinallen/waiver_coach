# prediction/

Contains scripts for actually making predictions

## rb_stats.py

Predicts RB stats for the next week (the week after nfldb currently thinks it is).

It can be configured to first training and testing on held out set, then predicting on the entire data set.

It can also be configured to load pickled python objects (think of these as cached) to make rerunning faster.

As of 10/30/2015, here are the results
	Predicting played
	Gradient Boosting: RMSE 0.39 | MAE 0.29
	Random Forest: RMSE 0.40 | MAE 0.29
	Logistic Regression: RMSE 0.39 | MAE 0.30

	Predicting receiving_rec
	Gradient Boosting: RMSE 1.63 | MAE 1.09
	Random Forest: RMSE 1.65 | MAE 1.08
	Linear Regression: RMSE 1.57 | MAE 1.07

	Predicting receiving_tds
	Gradient Boosting: RMSE 0.22 | MAE 0.09
	Random Forest: RMSE 0.22 | MAE 0.09
	Linear Regression: RMSE 0.22 | MAE 0.09

	Predicting receiving_yds
	Gradient Boosting: RMSE 14.23 | MAE 9.23
	Random Forest: RMSE 15.28 | MAE 9.23
	Linear Regression: RMSE 14.52 | MAE 9.41

	Predicting rushing_att
	Gradient Boosting: RMSE 5.64 | MAE 3.94
	Random Forest: RMSE 5.75 | MAE 3.94
	Linear Regression: RMSE 5.60 | MAE 3.93

	Predicting rushing_tds
	Gradient Boosting: RMSE 0.46 | MAE 0.25
	Random Forest: RMSE 0.46 | MAE 0.25
	Linear Regression: RMSE 0.46 | MAE 0.26

	Predicting rushing_yds
	Gradient Boosting: RMSE 28.55 | MAE 19.45
	Random Forest: RMSE 29.33 | MAE 19.61
	Linear Regression: RMSE 28.07 | MAE 19.24

## rushing_yards.py

Old simple code for predicting rushing yards. Made obsolete by rb_stats.py.

## rb_web_data.py
Used to make predictions based on stat projections scraped from the web. Currently only prints a dataframe with data from the web joined to data from nfldb.
