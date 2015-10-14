import nfldb

def week_team_list(db, season_year, week, season_type='Regular'):
	# returns list of teams playing in the specified week
	games = nfldb.Query(db).game(season_year=cur_year, week=week, season_type='Regular').as_games()
	teams = [tm for gm in games for tm in [gm.home_team, gm.away_team]]
	teams.sort()
	return teams

def players2dict(players):
	return [{field:getattr(plyr,field) for field in plyr.sql_fields()} for plyr in players]


db = nfldb.connect()
q = nfldb.Query(db)

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