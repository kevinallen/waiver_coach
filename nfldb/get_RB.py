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
match_list = []

for yr, wk in yr_wk:
	q = nfldb.Query(db)
	q.game(season_year=yr, week=wk, season_type='Regular')

	for games in q.as_games():
		match = {'year':yr, 'week':wk}
		match['home'] = games.home_team
		match['away'] = games.away_team
		match_list += [match]

	q.player(position='RB')	
	for pp in q.as_aggregate():
		pobj = {'year':yr, 'week':wk}
		for field in player_info:
			pobj[field] = getattr(pp.player,field)
		for field in stats:
			pobj[field] = getattr(pp,field)
		
		for match in match_list:
			if match['home'] == pobj['team']:
				pobj['home'] = match['home']
				pobj['away'] = match['away']
				pobj['homeaway'] = 1
			if match['away'] == pobj['team']:
				pobj['home'] = match['home']
				pobj['away'] = match['away']
				pobj['homeaway'] = 0
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

pdf_conv.to_csv('raw.csv')

