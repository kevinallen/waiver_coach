## feautre_extraction.py
Contains several Transformers that implement the scikit-learn `Transformer` class for manipulating input data and extracting features.

### WeeklyPlayerData
Extracts several weeks of player data from nfldb where X is the player_ids required. If no X is providedit gets all players for the requested qeeks

### LagPlayerData
Lags player data (as output from WeeklyPlayerData) to create lagged statistical features for players

### MeanPlayerData
Includes features that represent lifetime means for the stats of the players included in the input data (X)

### ExtractColumns
Only keeps particular columns, can be specificed 'like' (regex) or 'exact'

### HandleNaN
Decides what to do with rows ith NaN's. Either drop the row or fill (with 0s)

### Filter Played Percent
Throws out rows if the player did not play more than a threshold percent of the past games

### AddNameKey
Adds a name_key column to a dataframe to allow joining nfldb data to other sources.
