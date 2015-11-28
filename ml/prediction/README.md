# prediction/

Contains scripts for actually making predictions

## rb_stats.py

Predicts RB stats for the specified week. There are flags to add a vegas adjustment, to query nfldb (instead of loading a pickled object), and to add expert projections scraped from the web to the output.

```
usage: rb_stats.py [-h] [-v] [-q] [-x] week

positional arguments:
  week                  week of 2015 season to predict stats for

optional arguments:
  -h, --help            show this help message and exit
  -v, --vegas_adjustment
                        adjust model output using Vegas data
  -q, --run_query       query nfldb instead of using cached data
  -x, --expert_projections
                        add expert projections to output
```

It can be configured to first training and testing on held out set, then predicting on the entire data set.


As of 11/27/2015, here are the results
	--------------------------------------------------
Historical Prediction: played
Gradient Boosting: RMSE 0.40 | MAE 0.30
Random Forest: RMSE 0.41 | MAE 0.30
Logistic Regression: RMSE 0.40 | MAE 0.31

--------------------------------------------------
Expert prediction:  receiving_rec
Gradient Boosting: RMSE 1.43 | MAE 1.00
Random Forest: RMSE 1.62 | MAE 1.10
Linear Regression: RMSE 1.45 | MAE 0.98
--------------------------------------------------
Historical Prediction: receiving_rec
Gradient Boosting: RMSE 1.69 | MAE 1.21
Random Forest: RMSE 1.73 | MAE 1.25
Linear Regression: RMSE 1.67 | MAE 1.21

--------------------------------------------------
Expert prediction:  receiving_tds
Gradient Boosting: RMSE 0.33 | MAE 0.15
Random Forest: RMSE 0.29 | MAE 0.14
Linear Regression: RMSE 0.31 | MAE 0.14
--------------------------------------------------
Historical Prediction: receiving_tds
Gradient Boosting: RMSE 0.23 | MAE 0.10
Random Forest: RMSE 0.25 | MAE 0.10
Linear Regression: RMSE 0.23 | MAE 0.11

--------------------------------------------------
Expert prediction:  receiving_yds
Gradient Boosting: RMSE 20.60 | MAE 12.79
Random Forest: RMSE 22.02 | MAE 14.10
Linear Regression: RMSE 19.62 | MAE 12.40
--------------------------------------------------
Historical Prediction: receiving_yds
Gradient Boosting: RMSE 17.62 | MAE 12.16
Random Forest: RMSE 19.26 | MAE 13.20
Linear Regression: RMSE 17.47 | MAE 12.35

--------------------------------------------------
Expert prediction:  rushing_att
Gradient Boosting: RMSE 4.29 | MAE 3.20
Random Forest: RMSE 3.95 | MAE 3.05
Linear Regression: RMSE 3.92 | MAE 2.92
--------------------------------------------------
Historical Prediction: rushing_att
Gradient Boosting: RMSE 4.67 | MAE 3.44
Random Forest: RMSE 4.95 | MAE 3.67
Linear Regression: RMSE 4.79 | MAE 3.63

--------------------------------------------------
Expert prediction:  rushing_tds
Gradient Boosting: RMSE 0.67 | MAE 0.41
Random Forest: RMSE 0.63 | MAE 0.38
Linear Regression: RMSE 0.61 | MAE 0.36
--------------------------------------------------
Historical Prediction: rushing_tds
Gradient Boosting: RMSE 0.51 | MAE 0.35
Random Forest: RMSE 0.55 | MAE 0.36
Linear Regression: RMSE 0.52 | MAE 0.36

--------------------------------------------------
Expert prediction:  rushing_yds
Gradient Boosting: RMSE 33.33 | MAE 22.12
Random Forest: RMSE 36.21 | MAE 23.49
Linear Regression: RMSE 30.96 | MAE 20.93
--------------------------------------------------
Historical Prediction: rushing_yds
Gradient Boosting: RMSE 29.02 | MAE 20.79
Random Forest: RMSE 29.29 | MAE 21.23
Linear Regression: RMSE 28.79 | MAE 21.07

## test_rb_stats.ipynb

Version of rb_stats.py in ipython notebook for testing

## rb_nn.py

Script to create nearest neighbor distributions for players

## test_rb_nn.ipynb

ipython notebook for testing rb_nn.py

## rushing_yards.py

Old simple code for predicting rushing yards. Made obsolete by rb_stats.py.

## rb_web_data.py
Used to make predictions based on stat projections scraped from the web.
