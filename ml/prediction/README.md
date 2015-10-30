# prediction/

Contains scripts for actually making predictions

## rb_stats.py

Predicts RB stats for the next week (the week after nfldb currently thinks it is).

It can be configured to first training and testing on held out set, then predicting on the entire data set.

It can also be configured to load pickled python objects (think of these as cached) to make rerunning faster.

## rushing_yards.py

Old simple code for predicting rushing yards. Made obsolete by rb_stats.py.
