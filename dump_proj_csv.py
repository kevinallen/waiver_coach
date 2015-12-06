import pandas as pd
from pymongo import MongoClient

client = MongoClient()
db = client.data

cursor = db.projections.find( { 'position': 'RB' }, { 'week': 1, 'name': 1, 'year': 1, 'source': 1, 'pts': 1 } )

df = pd.DataFrame(list(cursor))
del df['_id']

df.to_csv('proj.csv')

