import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin

def webprojections_2dataframe(db, position=None, stats=[]):
    """Returns projections scraped from web as pandas dataframe.

    Args:
        db (pymongo.database.Database): MongoDB database with scraped data
        position (string): Position to include, for now just 'RB'
        stats (list[str]): Projected stats to include in dataframe

    Returns:
        pandas.DataFrame: All projected stats scraped from the web
    """

    # set a default position if none specified
    if position == None:
        position = 'RB'

    # choose which columns to select
    playerinfo = {'name':1,'name_key':1,'team':1,'position':1,'year':1,
        'week':1}
    # build dictionary of columns to keep in mongodb query
    stats = {stat: 1 for stat in stats}
    # keep source separate to make later logic easier
    columns = {'source':1}
    columns.update(playerinfo)
    columns.update(stats)

    rbs = db.projections.find({'position':position}, columns)
    df = pd.DataFrame(list(rbs))
    del df['_id']
    df.replace({'-':np.nan}, inplace=True)

    # group all sources of data for each player together
    grouped = df.groupby(['name_key','week'], axis=0)
    new_df = []
    for i,(name,group) in enumerate(grouped):
        cols = group.columns
        new_row = []
        new_labels = [col for col in playerinfo]
        includeinfo = True
        # each row from a separate source
        for _,row in group.iterrows():
            # only include player info once
            if includeinfo:
                new_row.extend(row[playerinfo].tolist())
                includeinfo = False
            # modify column labels and combine all rows to in a single row
            source = row['source'] + "_"
            # we only want to grab stat columns (not player details)
            stat_labels = [source + stat for stat in stats if stat in cols]
            new_labels.extend(stat_labels)
            row = row[stats].tolist()
            new_row.extend(row)

        # create list of dicts to use for creating a dataframe
        player = dict(zip(new_labels,new_row))
        new_df.append(player)

    new_df = pd.DataFrame(new_df)
    return new_df

def vegas_2dataframe(db, columns):
    # specify which columns to return
    if columns is not None:
        columns = {col: 1 for col in columns}
    else:
        columns = {}

    data = db.vegas.find(columns)
    df = pd.DataFrame(list(data))
    del df['_id']

    return df

class ProjectedPlayerData(TransformerMixin):
	def __init__(self, db, position=None, stats=[]):
		self.db=db
		self.stats = stats
		self.position = position
	# fit function essentially says do nothing
	def fit(self, *args, **kwargs):
		return self
	def transform(self, X=None):
		# X does nothing for this function
		# this function essentially pulls data
		# However, may change that later - X may
		# be a list of player names to get or something
		return webprojections_2dataframe(db=self.db, stats=self.stats, position=self.position)
	def get_params(self, deep=True):
		return {'stats':self.stats}
	def set_params(self, **parameters):
		for parameter, value in parameters.items():
			setattr(self, parameter, value)
		return self

class VegasData(TransformerMixin):
    def __init__(self, db, columns=None):
        self.db = db
        self.columns = columns
    def fit(self, *args, **kwargs):
        return self
    def transform(self, X=None):
        return vegas_2dataframe(db=self.db, columns=self.columns)
    def get_params(self, deep=True):
        return None
    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self

### Example usage
if False:
    client = MongoClient()
    mdb = client.data

    include_stats = ['fumbles','receptions','rec_yds','rec_tds',
                     'rush_attempts','rush_yds','rush_tds']
    projected = webprojections_2dataframe(mdb, stats=include_stats)
