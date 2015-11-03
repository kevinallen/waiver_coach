import numpy as np
import pandas as pd

# Get stats scraped from web for current year
def webprojections_2dataframe(db, position='RB', stats=[]):
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

### Example usage
if False:
    client = MongoClient()
    mdb = client.data

    include_stats = ['fumbles','receptions','rec_yds','rec_tds',
                     'rush_attempts','rush_yds','rush_tds']
    projected = webprojections_2dataframe(mdb, stats=include_stats)
