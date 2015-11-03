from ml.feature_extraction.nfldb_feature_extraction import WeeklyPlayerData
from ml.feature_extraction.nfldb_feature_extraction import AddNameKey
from sklearn.pipeline import Pipeline
from pymongo import MongoClient
import ml.mongo_helpers.web_helpers as wh
import pandas as pd
import nfldb

def main():
    # get historical data
    db = nfldb.connect()

    yr_wk = [(2015, i) for i in range(1,8)]
    stats = ['receiving_rec', 'receiving_tar', 'receiving_tds', 'receiving_yac_yds', 'receiving_yds', 'rushing_att', 'rushing_tds','rushing_yds']
    player_info = ['player_id','full_name','position']
    position = 'RB'

    playerdata = WeeklyPlayerData(db=db, yr_wk=yr_wk, stats=stats, player_info=player_info, fill_time=True, position=position)

    pipe = Pipeline(steps=[('data',playerdata), ('key',AddNameKey())])
    histdata = pipe.fit_transform(X=None)

    # get projected data
    client = MongoClient()
    mdb = client.data

    include_stats = ['fumbles','receptions','rec_yds','rec_tds',
                 'rush_attempts','rush_yds','rush_tds']
    projected = wh.webprojections_2dataframe(mdb, stats=include_stats)

    # join the two dataframes
    df = pd.merge(projected, histdata, how="inner", on=["name_key","week","year"])

    print df.head

if __name__ == '__main__':
    main()
