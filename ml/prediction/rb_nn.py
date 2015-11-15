###################
### Use nearest neighbors to find predicted distributions of players
###################

##########
### Dependencies

import nfldb
import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import os

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


#############
### Function for plotting KNN distributinos and saving them

def plot_knn(nn_df, plot_stat, pred_yr_wk, result_path, n_bins=2, bandwidth=2.5, save_id = True, save_time = False, save_stat = True):
    # the histogram of the data
    stat_X = nn_df.iloc[1:][plot_stat]
    player_name = nn_df.iloc[0]['full_name']
    player_id =  nn_df.iloc[0]['player_id']
    n, bins, patches = plt.hist(stat_X, n_bins, normed=1, edgecolor='none', facecolor='grey', alpha=0.25)

    # get plot limits
    xmin = 0
    xmax = max(bins)*1.1
    ymin = 0
    ymax = max(n)*1.1

    # get bins for kernel density plot
    bins = np.linspace(xmin, xmax, 100)

    # set up kernel density
    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(X=stat_X[:,np.newaxis])
    y_smooth = np.exp(kde.score_samples(bins[:,np.newaxis]))
    y_smooth

    l = plt.plot(bins, y_smooth, 'b--', linewidth=1)
    plt.xlabel(plot_stat)
    plt.ylabel('Probability')
    plt.axis([0, max(bins)*1.1, 0, max(n)*1.1])
    plt.title(player_name)
    plt.grid(True)

    if not os.path.exists(result_path):
    	os.makedirs(result_path)

    save_path = result_path + '/'
    fname_list = []
    if save_id:
    	fname_list += [player_id]
    else:
    	fname_list += [player_name]

    if save_time:
    	fname_list += [str(pred_yr_wk[0]), str(pred_yr_wk[1])]

    if save_stat:
    	fname_list += [plot_stat]

    save_path += '_'.join(fname_list) + '.png'

    plt.savefig(save_path)
    plt.close()

def main():
	################################
	### CONFIGURE
	pred_week = 10 #None
	db = nfldb.connect()
	result_path='../results'

	### LOAD DATA
	# load train data
	full_train, pipe, stats = load_feature_set(db)

	# picks columns to model
	lag_cols = [stat + '_lag' for stat in stats]
	mean_cols = [stat + '_mean' for stat in stats]
	other_cols = ['same_year_lag', 'played_lag']

	infoColumns = ExtractColumns(like=[], exact=['year','week','time','player_id','full_name'])
	row_info = infoColumns.fit_transform(X=full_train)

	# load prediction data
	pred_data, predict_i, pred_info, pred_yr_wk = prediction_feature_set(db, pipe, infoColumns, pred_week=pred_week)

	##################################
	### PREPARE DATA FOR TRAIN AND PREDICT
	# train data with all columns
	X_all = full_train

	# prediction data with all columns
	pred_all = pred_data.iloc[predict_i]

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

	###### THIS SECTION NOT NEED FOR KNN - MAY USE IN STAT PREDICTION
	# y_col = 'receiving_yds'

	# y = X_all[y_col]

	# if(played_only and y_col != 'played'):
	#     train_i = list(set.intersection(set(train_index), set(played_index)))
	#     test_i = list(set.intersection(set(test_index), set(played_index)))
	# else:
	#     train_i = train_index
	#     test_i = test_index

	# X_train = X.iloc[train_i]
	# y_train = y.iloc[train_i]
	# X_test = X.iloc[test_i]
	# y_test = y.iloc[test_i]

	##################################
	### SET UP & TRAIN KNN
	# fit k nearest neighbors
	k = 100
	played_only = True
	i_knn = played_index if played_only else range(X.shape[0])
	    
	nn = NearestNeighbors(n_neighbors=k).fit(X.iloc[i_knn])

	# returns tuple of (distances, indices of neighbors)
	# for prediction set
	distance, neighbor = nn.kneighbors(X=X_pred)

	##################################
	### READ AND PLOT KNN RESULTS
	for check_i in range(pred_all.shape[0]):
	    # check neighbors
	    # check_nn is a data frame where the first row is the player
	    # and the rest of the rows are the nearest neighbors
	    check_nn = pred_all.iloc[[check_i],:].append(X_all.iloc[i_knn].iloc[neighbor[check_i,:]])
	    check_nn['StandardPoints'] = score_stats(check_nn, make_scorer(base_type='standard'))
	    check_nn['PPRPoints'] = score_stats(check_nn, make_scorer(base_type='ppr'))
	    
	    plot_knn(check_nn, plot_stat='StandardPoints', pred_yr_wk=pred_yr_wk, result_path=result_path+'/knn/distimages/'+str(pred_yr_wk[1]), n_bins=25, bandwidth=2.5)


if __name__ == "__main__":
	main()


