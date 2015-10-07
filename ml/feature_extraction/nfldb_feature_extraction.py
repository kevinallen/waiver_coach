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
	group['played'] = pd.isnull(group['player_id']) == False
	# pad player_info
	player_info = ['player_id','full_name','position']
	group[player_info] = group[player_info].fillna(method='pad')
	# 0 for all stats
	stats = ['rushing_yds','rushing_att']
	group[stats] = group[stats].fillna(0)
	# add year week for all
	yr_wk_df = pd.DataFrame(list(pd.Series(all_t).apply(inverse_rs_time)), index=all_t)
	yr_wk_col = list(yr_wk_df.columns.values)
	group[yr_wk_col] = yr_wk_df
	# return
	return group



# takes a nfldb database link (db) and returns a dataframe
# where each row is a plyear in a year in a week
# yr_wk is a list of (year, week) tuples
# stats is a list of stats to pull from each PlayPlayer
# player_info is a list of information to pull for each player
# position is a position to filter for
# returns the data frame indexed by rs_time (regular season time)
# fill_time indicates whether to fill missing time in the player's career with 0 stats
# if fill_time == True it also creates a binary feature called 'played'
def player_week2dataframe(db, yr_wk, stats, player_info, position='RB', fill_time=True):
	player_list = []
	for yr, wk in yr_wk:
		# query for this weak
		q = nfldb.Query(db)
		# filter for year, week, and regular season
		q.game(season_year=yr, week=wk, season_type='Regular')
		# maybe filter for position
		if(position):
			q.player(position=position)	
		# loop through PlayPlayer objects, aggregated for the week
		for pp in q.as_aggregate():
			pobj = {'year':yr, 'week':wk}
			for field in player_info:
				pobj[field] = getattr(pp.player,field)
			for field in stats:
				pobj[field] = getattr(pp,field)
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
	re_pat = re.compile('|'.join(like))
	col_names = df.columns.values.tolist()
	col_matches = [col for col in col_names if re_pat.search(col)]
	col_matches.extend([col for col in exact if (not(col in col_matches) and col in col_names)])
	return df[col_matches]

def drop_nan(df):
	return(df.dropna(axis=0))


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
		return player_week2dataframe(db=self.db, yr_wk=self.yr_wk, stats=self.stats, fill_time=self.fill_time, player_info=self.player_info, position=self.position)
	def get_params(self, deep=True):
		return {}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			self.setattr(parameter, value)
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
		return {}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			self.setattr(parameter, value)
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
			self.setattr(parameter, value)
		return self


class DropNaN(TransformerMixin):
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X):
		return drop_nan(X)
	def get_params(self, deep=True):
		return {}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			self.setattr(parameter, value)
		return self


