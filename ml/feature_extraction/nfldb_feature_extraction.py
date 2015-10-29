import nfldb
import pandas as pd
import numpy as np
import re
import math

from sklearn.base import TransformerMixin

# rs_time stands for regular season time
# this is elapsed weeks of regular season
# since the 1970 merger. It's currently
# incorrect on an absolute basis because there
# have not been 17 weeks every year, but
# it is correct on a relative basis recently
def rs_time(year, week, base_year=1970):
	return ((year - base_year)*17 + week)

# takes year and week and returns the rs_time
def inverse_rs_time(rs_t, base_year=1970):
	year = int(math.floor((rs_t-1)/17 + base_year))
	week = rs_t - (year - base_year)*17
	if(rs_time(year, week, base_year) == rs_t):
		return {'year':year,'week':week}
	else:
		raise ValueError('the result of inverse_rs_time is not consistent with rs_time')

# used like df.apply(rs_time_df, 1) to get time for each row of df
def rs_time_df(obj, base_year=1970):
	return rs_time(year=obj.year, week=obj.week, base_year=base_year)

# this function fills in missing weeks for each player and
# creates a variable called "played"
def fill_time_of_group(group, stats, player_info, group_by='player_id'):


	#groups = data.groupby(['player_id'])
	#groups.apply(fill_time_of_group, stats=stats, player_info=player_info, group_by='player_id')
	#groups = dict(list(groups))
	#group = groups[groups.keys()[0]]
	used_t = group.index
	all_t = range(min(used_t), max(used_t)+1)
	# add rows for missing times
	group = group.reindex(all_t)
	# wherever player_id is missing, create feature called played=0, else played=1
	#group['played'] = pd.isnull(group['player_id']) == False
	group['played'] = group['played'].fillna(False)
	# pad player_info
	#player_info = ['player_id','full_name','position']
	group[player_info] = group[player_info].fillna(method='pad')
	# 0 for all stats
	group[stats] = group[stats].fillna(0)
	# add year week for all
	yr_wk_df = pd.DataFrame(list(pd.Series(all_t).apply(inverse_rs_time)), index=all_t)
	yr_wk_col = list(yr_wk_df.columns.values)
	group[yr_wk_col] = yr_wk_df
	# return
	return group

# GOAL: get all yr_wk asked for all player_ids, 0ing any stats for weeks that were skipped

# takes a nfldb database link (db) and returns a dataframe
# where each row is a player in a year in a week
# yr_wk is a list of (year, week) tuples
# stats is a list of stats to pull from each PlayPlayer
# player_info is a list of information to pull for each player
# position is a position to filter for
# returns the data frame indexed by rs_time (regular season time)
# fill_time indicates whether to fill missing time in the player's career with 0 stats
# if fill_time == True it also creates a binary feature called 'played'
# if player_ids is specified, it WILL return stats for those players for EVERY yr_wk asked for
# even if a player wasn't an active NFL player at the time - the stats will just be 0.
def player_week2dataframe(db, yr_wk, stats, player_info, player_ids=None, position='RB', fill_time=True):
	player_list = []
	player_objects = {player.player_id:player for player in nfldb.Query(db).player(player_id=player_ids).as_players()}

	for yr, wk in yr_wk:
		# query for this weak
		q = nfldb.Query(db)
		# filter for year, week, and regular season
		q.game(season_year=yr, week=wk, season_type='Regular')
		# maybe filter for position
		if(position):
			q.player(position=position)
		if(player_ids):
			q.player(player_id=player_ids)
			# create copy of player_ids to remove as handled
			player_ids_i = list(player_ids)
		# loop through PlayPlayer objects, aggregated for the week
		for pp in q.as_aggregate():
			player = pp.player
			pobj = {'year':yr, 'week':wk}
			pid = player.player_id
			for field in player_info:
				pobj[field] = getattr(player,field)
			for field in stats:
				pobj[field] = getattr(pp,field)
			pobj['played'] = True
			player_list += [pobj]
			if(player_ids):
				player_ids_i.remove(pid)
		if(player_ids):
			for pid in player_ids_i:
				player = player_objects[pid]
				pobj = {'year':yr, 'week':wk}
				for field in player_info:
					pobj[field] = getattr(player,field)
				for field in stats:
					pobj[field] = np.nan
				pobj['played'] = False
				player_list += [pobj]
	pdf = pd.DataFrame(player_list)
	pdf['time'] = pdf.apply(rs_time_df, 1)
	pdf.set_index('time', inplace=True)

	if(fill_time):
		groupby_col = 'player_id'
		# fills in missing time & creates played
		pdf = pdf.groupby(groupby_col).apply(fill_time_of_group, stats=stats, player_info=player_info, group_by='player_id')


	return(pdf)


def make_lag_data_group(df, lag_cols, nlag=4, same_year_bool=True):
	def lag_str(col, i):
		return col + '_lag' + str(i);
	dfout = df
	for i in range(1,nlag+1):
		dfi = df[lag_cols].shift(i)
		dfi.columns = [lag_str(col, i) for col in dfi.columns]
		dfout = pd.concat([dfout, dfi], axis=1)
		if(same_year_bool):
			yr_lag = lag_str('year', i)
			dfout[lag_str('same_year',i)] = dfout['year'] == dfout[yr_lag]
			dfout.loc[pd.isnull(dfout[yr_lag]),lag_str('same_year',i)] = np.nan
	return dfout

def make_lag_data(df, lag_cols, nlag=4, groupby_cols = ['player_id'], same_year_bool=True):
	grouped = df.groupby(groupby_cols)
	df_lag=None
	for name, group in grouped:
		dfi = make_lag_data_group(group, nlag=nlag, lag_cols=lag_cols, same_year_bool=same_year_bool)
		if(df_lag is None):
			df_lag = dfi
		else:
			df_lag = pd.concat([df_lag, dfi], axis=0)
	return(df_lag)

# chooses columns that match the patterns in like
def pick_columns(df, like=[], exact=[]):
	col_names = df.columns.values.tolist()
	if(len(like) != 0):
		re_pat = re.compile('|'.join(like))
		col_matches = [col for col in col_names if re_pat.search(col)]
	else:
		col_matches = []
	col_matches.extend([col for col in exact if (not(col in col_matches) and (col in col_names))])
	return df[col_matches]

def drop_nan(df):
	return(df.dropna(axis=0))

def fill_nan(df, value=0):
	return(df.fillna(value=value))

### Make variable that captures average of group
def make_mean_data_group(df, mean_cols, start_at_first_played=True):
	def col_str(col):
		return col + '_mean';
	# start the mean at the first played game
	if start_at_first_played and ('played' in df.columns):
		# find the index of the first played game
		# player may have never played:
		if df['played'].any():
			first_played = df['played'].ravel().nonzero()[0][0]
		else:
			first_played = -1
	else:
		first_played = df.index[0]


	dfout = df[mean_cols].copy()
	if first_played == -1:
		# special case that the player has never played before
		dfout[:] = 0
	else:
		# get the mean
		dfout.iloc[first_played:] = pd.rolling_mean(dfout.iloc[first_played:].fillna(value=0), min_periods=0, window=10000000)
		# set the mean to zero before that game
		dfout.iloc[:first_played] = 0

	dfout.columns = [col_str(col) for col in dfout.columns]
	dfout = pd.concat([df, dfout], axis=1)
	return dfout

### Make variable that captures average of group
def make_mean_data(df, mean_cols, groupby_cols = ['player_id'], start_at_first_played=True):
	grouped = df.groupby(groupby_cols)
	df_out=None
	for name, group in grouped:
		dfi = make_mean_data_group(group, mean_cols=mean_cols)
		if(df_out is None):
			df_out = dfi
		else:
			df_out = pd.concat([df_out, dfi], axis=0)
	return(df_out)

### Set a threshold for played percent on lagged data
# if they didnt play in more than pct_played_threshold*n of the n lagged games
# the row gets thrown out
def filter_played_percent(df, pct_played_threshold):
	if(pct_played_threshold <= 0):
		return df
	if(pct_played_threshold > 1):
		raise ValueError('pct_played_threshold of more than 1 will throw out all observations')
	re_pat = re.compile('played_lag')
	col_names = df.columns.values.tolist()
	col_matches = [col for col in col_names if re_pat.search(col)]
	return df[df[col_matches].fillna(value=0).mean(axis=1) >= pct_played_threshold]

### Add column to dataframe to use as a unique key to join
# other datasets (e.g., projections scraped from web).
# Creates a name_key when passed a dataframe row-wise
def make_name_key(df):
    full_name = df['full_name']
    pos = df['position']
    name_key = re.sub(r"[\.,\s\']","", full_name).upper()
    if (name_key,pos) in duplicates:
        name_key = duplicates[(name_key,pos)]
    return name_key

class WeeklyPlayerData(TransformerMixin):
	def __init__(self, db, yr_wk=None, fill_time=True, stats=[], player_info=['player_id','full_name','position'],position=None):
		self.db=db
		if(yr_wk):
			self.yr_wk = yr_wk
		else:
			self.yr_wk = [(j, i) for j in [2009,2010,2011,2012,2013,2014,2015] for i in range(1,18)]
		self.player_info = player_info
		self.stats = stats
		self.position = position
		self.fill_time=fill_time
	# fit function essentially says do nothing
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X=None):
		# X does nothing for this function
		# this function essentially pulls data
		# However, may change that later - X may
		# be a list of player names to get or something
		return player_week2dataframe(player_ids=X, db=self.db, yr_wk=self.yr_wk, stats=self.stats, fill_time=self.fill_time, player_info=self.player_info, position=self.position)
	def get_params(self, deep=True):
		return {'stats':self.stats, 'player_info':self.player_info}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			setattr(self, parameter, value)
		return self

class LagPlayerData(TransformerMixin):
	def __init__(self, nlag=4, groupby_cols=['player_id'], lag_cols=[], same_year_bool=True):
		if(same_year_bool and not('year' in lag_cols)):
			lag_cols.append('year')
		self.nlag = nlag
		self.groupby_cols = groupby_cols
		self.lag_cols = lag_cols
		self.same_year_bool = same_year_bool
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X):
		return make_lag_data(X, nlag=self.nlag, groupby_cols=self.groupby_cols, lag_cols=self.lag_cols, same_year_bool=self.same_year_bool)
	def get_params(self, deep=True):
		return {'lag_cols':self.lag_cols}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			setattr(self, parameter, value)
		return self

class MeanPlayerData(TransformerMixin):
	def __init__(self, groupby_cols=['player_id'], mean_cols=[]):
		self.groupby_cols = groupby_cols
		self.mean_cols = mean_cols
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X):
		return make_mean_data(X, groupby_cols=self.groupby_cols, mean_cols=self.mean_cols)
	def get_params(self, deep=True):
		return {'mean_cols':self.mean_cols}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			setattr(self, parameter, value)
		return self

class ExtractColumns(TransformerMixin):
	def __init__(self, like=[], exact=[]):
		self.like = like
		self.exact = exact
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X):
		return pick_columns(X, like=self.like, exact=self.exact)
	def get_params(self, deep=True):
		return {}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			setattr(self, parameter, value)
		return self


class HandleNaN(TransformerMixin):
	def __init__(self, method='fill'):
		# method should be fill or drop
		self.method = method
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X):
		if(self.method == 'drop'):
			return drop_nan(X)
		elif(self.method == 'fill'):
			return fill_nan(X)
		else:
			raise ValueError('HandleNaN method must be "drop" or "fill" not ' + str(self.method))
	def get_params(self, deep=True):
		return {}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			setattr(self, parameter, value)
		return self

class FilterPlayedPercent(TransformerMixin):
	def __init__(self, pct_played_threshold=0.0):
		self.pct_played_threshold = pct_played_threshold
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X):
		return filter_played_percent(X, self.pct_played_threshold)
	def get_params(self, deep=True):
		return {}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			setattr(self, parameter, value)
		return self

class AddNameKey(TransformerMixin):
	def __init__(self):
		pass
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X):
		name_keys = X.apply(make_name_key, axis=1)
		X.loc[:,'name_key'] = pd.Series(name_keys)
		return X
	def get_params(self, deep=True):
		return {}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			setattr(self, parameter, value)
		return self
