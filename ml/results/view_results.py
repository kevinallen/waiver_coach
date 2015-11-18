import pandas as pd

result_file = 'predictions_2015_6.json'

pred = pd.read_json(result_file, orient='records')