import nfldb
import pandas as pd
import numpy as np
import re

db = nfldb.connect()
q = nfldb.Query(db)

yr_wk = [(j, i) for j in [2012,2013,2014,2015] for i in range(1,18)]

stats = ['rushing_yds','rushing_att','rushing_tds','receiving_yds','receiving_tar','receiving_rec','receiving_tds','fumbles_lost']
player_info = ['player_id','full_name','position','team']

player_list = []
for yr, wk in yr_wk:
	q = nfldb.Query(db)
	q.game(season_year=yr, week=wk, season_type='Regular').player(position='RB')	
	for pp in q.as_aggregate():
		pobj = {'year':yr, 'week':wk}
		for field in player_info:
			pobj[field] = getattr(pp.player,field)
		for field in stats:
			pobj[field] = getattr(pp,field)
		player_list += [pobj]


# rs stands for regular season time
# this is elapsed weeks of regular season
# since the 1970 merger. It's currently
# incorrect on an absolute basis because there
# have not been 17 weeks every year, but
# it is correct on a relative basis recently
def rs_time(year, week, base_year=1970):
	return ((year - base_year)*17 + week)

def rs_time_df(obj, base_year=1970):
	return rs_time(year=obj.year, week=obj.week, base_year=base_year)


pdf = pd.DataFrame(player_list)
pdf['time'] = pdf.apply(rs_time_df, 1)
pdf.set_index('time', inplace=True)

tds_conv = 60
pdf_conv = pdf
for col in ['rushing_tds','receiving_tds']:
	pdf_conv[col] = pdf[col] * tds_conv

#grouped = pdf.groupby('player_id')

pdf.to_csv('raw.csv')
#grouped.to_csv('grouped.csv')


#def make_lag_data_group(df, nlag=4, cols=['year', 'week', 'rushing_att', 'rushing_yds', 'rushing_loss_yds', 'rushing_tds'], same_year_bool=True):
#	def lag_str(col, i):
#		return col + '_lag' + str(i);
#	dfout = df
#	for i in range(1,nlag+1):
#		dfi = df[cols].shift(i)
#		dfi.columns = [lag_str(col, i) for col in dfi.columns]
#		dfout = pd.concat([dfout, dfi], axis=1)
#		if(same_year_bool):
#			yr_lag = lag_str('year', i)
#			dfout[lag_str('same_year',i)] = dfout['year'] == dfout[yr_lag]
#			dfout.loc[pd.isnull(dfout[yr_lag]),lag_str('same_year',i)] = np.nan
#	return dfout



#def make_lag_data(df, nlag=4, groupby_cols = ['player_id'], cols=['year', 'week', 'rushing_att', 'rushing_yds']):
#	grouped = df.groupby(groupby_cols)
#	df_lag=None
#	for name, group in grouped:
#		dfi = make_lag_data_group(group, nlag=nlag)
#		if(df_lag is None):
#			df_lag = dfi
#		else:
#			df_lag = pd.concat([df_lag, dfi], axis=0)
#	return(df_lag)

#def pick_columns(df, like=['rushing_yds','rushing_yds_lag','rushing_att_lag','same_year_lag']):
#	re_pat = re.compile('|'.join(like))
#	col_names = df.columns.values.tolist()
#	col_matches = [col for col in col_names if re_pat.search(col)]
#	return df[col_matches]
#
#def drop_nan(df):
#	return(df.dropna(axis=0))



#pdf_lag = make_lag_data(pdf, nlag=4)
#pdf_lag = pick_columns(pdf_lag)
#pdf_lag = drop_nan(pdf_lag)


#def train_test_split_index(n,test_size=0.2):
#	rand_i = np.random.choice(range(n), n, replace=False)
#	test_i = rand_i[range(int(round(n*test_size)))]
#	train_i = rand_i[range(int(round(n*test_size)),n)]
#	return train_i, test_i



#y_col = 'rushing_yds'
#y = pdf_lag[y_col]
#X = pdf_lag.drop(y_col, axis=1)

#train_i, test_i = train_test_split_index(X.shape[0], test_size=0.2)

#y_train = y.iloc[train_i]
#y_test = y.iloc[test_i]
#X_train = X.iloc[train_i]
#X_test = X.iloc[test_i]


#from sklearn.cross_validation import train_test_split
#from sklearn.ensemble import GradientBoostingRegressor


#pdf_lag.head()



