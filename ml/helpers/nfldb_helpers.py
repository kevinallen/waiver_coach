import nfldb
import pandas as pd

def week_team_list(db, season_year, week, season_type='Regular'):
	# returns list of teams playing in the specified week
	games = nfldb.Query(db).game(season_year=season_year, week=week, season_type='Regular').as_games()
	teams = [tm for gm in games for tm in [gm.home_team, gm.away_team]]
	teams.sort()
	return teams

def week_player_list(db, season_year, week, season_type='Regular', position=None):
	# returns a list of players objects who are on teams playing in the specified week
	week_teams = week_team_list(db=db, season_year=season_year, week=week, season_type=season_type)
	q = nfldb.Query(db).player(team=week_teams)
	if position:
		q = nfldb.Query(db).player(position=position)
	players = q.as_players()
	return players

def week_player_id_list(db, season_year, week, season_type='Regular', position=None):
	week_players = week_player_list(db=db, season_year=season_year, week=week, season_type=season_type, position=position)
	return [player.player_id for player in week_players]

def player_id2player(id_list):
	return nfldb.Query(db).player(player_id=id_list).as_players()

def players2dict(players):
	return [{field:getattr(plyr,field) for field in plyr.sql_fields()} for plyr in players]

def player_id2dict(id_list):
	return players2dict(player_id2player(id_list))

def player_game_info(db, player_ids = [], as_DataFrame = True, use_current_team = False, yr_wk=[]):
	# this function gets information for every game this player has played
	if not use_current_team:
		var_query = '''
		SELECT DISTINCT
		  player.full_name, play_player.player_id, play_player.team, play_player.gsis_id, game.home_team, game.away_team, game.week, game.season_year as year
		FROM play_player
		LEFT JOIN game ON play_player.gsis_id = game.gsis_id
		LEFT JOIN player ON play_player.player_id = player.player_id
		WHERE player.player_id IN %s
		'''
	else:
		var_query = '''
		SELECT DISTINCT
		  player.full_name, player.player_id, player.team, game.gsis_id, game.home_team, game.away_team, game.week, game.season_year as year
		FROM player
		LEFT JOIN game ON (player.team = game.home_team OR player.team = game.away_team)
		WHERE player.player_id IN %s
		'''
	# string for player id WHERE clause
	where_str = "('"+"','".join(player_ids)+"')"
	if len(yr_wk) > 0:
		yr_wk_str = " OR ".join(['(game.season_year = ' + str(yr_wk_i[0]) + ' AND game.week = ' + str(yr_wk_i[1]) +")" for yr_wk_i in yr_wk])
		where_str += " AND (" + yr_wk_str + ")"
	# final query
	query = var_query % where_str
	players = []
	with nfldb.Tx(db) as cursor:
	    cursor.execute(query)
	    for row in cursor.fetchall():
	        pp = row
	        players.append(pp)
	# create some derived information
	for player in players:
		# set the opponent team & whether player was at home
		player['at_home'] = player['home_team'] == player['team']
		if player['at_home']:
			player['opp_team'] = player['away_team']
		else:
			player['opp_team'] = player['home_team']
	# make in to DataFrame
	if as_DataFrame:
		players = pd.DataFrame(players)
	return(players)

# Need two functions to get player info like team and opposing team

# One to take a list of of PlayPlayers and find the team THAT WEEK & opposing team THAT WEEK
## This is useful for building training data
def player_all_game_info(db, player_ids=[], as_DataFrame=True):
	return(player_game_info(db, player_ids, yr_wk=[], as_DataFrame=as_DataFrame, use_current_team=False))

# Another to take a list of player_ids & year & week and find the CURRENT team & opposing team THAT WEEK
## This is useful for building actual predictions
def player_current_game_info(db, year, week, player_ids=[], as_DataFrame=True):
	return(player_game_info(db, player_ids, yr_wk=[(year, week)], as_DataFrame=as_DataFrame, use_current_team=True))

def player_team_info(db):
	query = '''
	SELECT 	pp.player_id,
			pp.team,
			g.season_year AS year,
			g.week
	FROM game g
	LEFT JOIN play_player pp on g.gsis_id = pp.gsis_id
	LEFT JOIN player p on pp.player_id = p.player_id
	WHERE g.season_type = 'Regular' AND p.position = 'RB'
	GROUP BY
			pp.player_id,
			pp.team,
			g.season_year,
			g.week;
	'''

	data = []
	with nfldb.Tx(db) as cursor:
	    cursor.execute(query)
	    for row in cursor.fetchall():
	        data.append(row)

	data = pd.DataFrame(data)
	return data

if False:

	players2dict(player_id2player(week_player_id_list(db, 2015, 6)))

	db = nfldb.connect()
	q = nfldb.Query(db)

	players2dict(player_id2player(week_player_id_list(db, 2015, 6)))

	# get current season phase, year, week
	season_phase, cur_year, cur_week = nfldb.current(db)

	pred_week = cur_week

	# master list of teams - all teams play in week 1
	all_teams = week_team_list(db, cur_year, week=1)

	# master list of players
	all_players = players2dict(nfldb.Query(db).player(team=all_teams).as_players())

	# list of teams playing for a week
	week_teams = week_team_list(db, cur_year, week=pred_week)

	# list of all players on those teams
	week_players = [plyr for plyr in all_players if plyr['team'] in week_teams]

	[plyr for plyr in all_players if plyr['full_name'] == 'Peyton Manning' ]

	# if player id's exist
	player_ids = ['00-0022803','00-0010346']

	if(player_ids):
		# get list of those players
		player_info = nfldb.Query(db).player(player_id=player_ids)


	# player id this week
	pps = nfldb.Query(db).player(player_id=player_ids).game(season_year=cur_year, week=cur_week).as_play_players()
	teams = [pp.team for pp in pps]

	player_game_info(player_ids, use_current_team=True, yr_wk=yr_wk)

	yr_wk = [(2015,6),(2015,5)]
	" OR ".join(['(game.season_year = ' + str(yr_wk_i[0]) + ' AND game.week = ' + str(yr_wk_i[1]) +")" for yr_wk_i in yr_wk])
