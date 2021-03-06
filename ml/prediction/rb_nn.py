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
import json

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
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KernelDensity
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.base import TransformerMixin



############
### Determines the path for distribution image plots
def plot_image_path(result_path, pred_yr_wk):
    return(result_path+'/knn/distimages/'+str(pred_yr_wk[0])+'_'+str(pred_yr_wk[1]))

############
### Determines the path and file name for plot data
def plot_data_path_file(result_path, pred_yr_wk):
    return([result_path+'/knn/distdata/',str(pred_yr_wk[0])+'_'+str(pred_yr_wk[1])+'.json'])

#############
### Function for plotting KNN distributinos and saving them
def plot_knn(nn_df, plot_stat, pred_yr_wk, result_path, n_bins=2, bandwidth=2.5, save_id = True, save_time = False, save_stat = True, save_image=True):
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
    smooth_bins = np.linspace(xmin, xmax, 100)

    # set up kernel density
    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(X=stat_X[:,np.newaxis])
    y_smooth = np.exp(kde.score_samples(smooth_bins[:,np.newaxis]))
    y_smooth

    l = plt.plot(smooth_bins, y_smooth, 'b--', linewidth=1)
    plt.xlabel(plot_stat)
    plt.ylabel('Probability')
    plt.axis([xmin, xmax, ymin, ymax])
    plt.title(player_name)
    plt.grid(True)
    
    if save_image:
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
        
        raw_bins = bins[1:]
        raw_data = [{'x':raw_bins[i],'y':n[i]} for i in range(len(raw_bins))]
        smooth_data = [{'x':smooth_bins[i],'y':y_smooth[i]} for i in range(len(y_smooth))]

    
    return({player_id:{'raw':raw_data, 'smooth':smooth_data, 'player_name':player_name, 'player_id':player_id}})

#############
### CoefScaler - multiplies values by their weight in some linear model

class CoefScaler(TransformerMixin):
    def __init__(self, linear_model):
        self.linear_model = linear_model
    def fit(self, X, y):
        self.linear_model = self.linear_model.fit(X, y)
        return self
    def transform(self, X):
        return X * self.linear_model.coef_
    def get_params(self, deep=True):
        return {}
    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self


############
### Function for saveing plot data as json to support web viz
def save_plot_data_json(nn_dict, result_path, pred_yr_wk):
    json_fp = plot_data_path_file(result_path, pred_yr_wk)

    if not os.path.exists(json_fp[0]):
                os.makedirs(json_fp[0])

    with open('/'.join(json_fp), 'w+') as fp:
        json.dump(nn_dict, fp)

def main():
	################################
	### CONFIGURE
	pred_week = 14 #None
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

	##################################
	### SET UP & TRAIN KNN
	# fit k nearest neighbors
	k = 100
	played_only = True
	i_knn = played_index if played_only else range(X.shape[0])

	#nn = NearestNeighbors(n_neighbors=k).fit(X.iloc[i_knn])
	# regularization
	reg = CoefScaler(linear_model=Ridge())
	reg = reg.fit(X=X.iloc[i_knn], y = score_stats(X_all, make_scorer(base_type='standard')).iloc[i_knn])
	X_reg = reg.transform(X.iloc[i_knn])
	nn = NearestNeighbors(n_neighbors=k).fit(X_reg)

	# returns tuple of (distances, indices of neighbors)
	# for prediction set
	#distance, neighbor = nn.kneighbors(X=X_pred)
	X_reg_pred = reg.transform(X=X_pred)
	distance, neighbor = nn.kneighbors(X=X_reg_pred)

	##################################
	### READ AND PLOT KNN RESULTS
	nn_dict = {}
	for check_i in range(pred_all.shape[0]):
	    # check neighbors
	    # check_nn is a data frame where the first row is the player
	    # and the rest of the rows are the nearest neighbors
	    check_nn = pred_all.iloc[[check_i],:].append(X_all.iloc[i_knn].iloc[neighbor[check_i,:]])
	    check_nn['StandardPoints'] = score_stats(check_nn, make_scorer(base_type='standard'))
	    check_nn['PPRPoints'] = score_stats(check_nn, make_scorer(base_type='ppr'))

	    nn_i = plot_knn(check_nn, save_image=True, plot_stat='StandardPoints', pred_yr_wk=pred_yr_wk, result_path=plot_image_path(result_path, pred_yr_wk), n_bins=25, bandwidth=2.5)
	    nn_dict.update(nn_i)

	save_plot_data_json(nn_dict, result_path, pred_yr_wk)


if __name__ == "__main__":
	main()


