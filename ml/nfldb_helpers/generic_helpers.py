import nfldb

def week_team_list(db, season_year, week, season_type='Regular'):
	# returns list of teams playing in the specified week
	games = nfldb.Query(db).game(season_year=season_year, week=week, season_type='Regular').as_games()
	teams = [tm for gm in games for tm in [gm.home_team, gm.away_team]]
	teams.sort()
	return teams

def week_player_list(db, season_year, week, season_type='Regular', position=None):
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


