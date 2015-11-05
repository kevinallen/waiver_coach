## generic_helpers.py
Contains several functions that are generically useful for intereacting with nfldb

Also contains a section for testing the functions.
### week_team_list
returns a list of teams playin in the specified week - useful for scheduling

### week_player_list
returns a list of player objects who are on teams that are playing in the specified week

### week_player_id_list
return a list of player_id's of players on teams that are playing in the specified week

### player_id2player
takes a player id and returns a player object

###players2dict
takes a list of player objects and returns a list of player dicts, where each dict has metadata about the player (team etc)

### player_id2dict
takes a list of player ids and returns a list of dicts of each player's info (team etc)

### player_game_info
takes a list of player_id's and returns list of dicts with metadata for every game this player has played.

This importantly includes the team they are one (team), the opponent team (opp_team), and whether they were home or away (at_home)

### player_all_game_info
Take a list of player_ids and find the team the player was on THAT WEEK & opposing team THAT WEEK for every week the player played.

This is useful for building training data

### player_current_game_info
Take a list of player_ids & year & week and find the CURRENT team & opposing team THAT WEEK

This is useful for building actual predictions
