import argparse
import os
import json
from ml.helpers.scoring_helpers import make_scorer
from ml.helpers.scoring_helpers import score_stats

def score_stats_dict(stat_dict, scorer=make_scorer(base_type='standard')):
    stat_dict.update({u'standard_score':sum([v*stat_dict[k] for k, v in scorer.iteritems() if k in stat_dict.keys()])})
    return stat_dict

def main(dist_file, pred_file, scoring_type):
    #dist_file = '2015_10.json'
    #pred_file = '../predictions.json'
    #scoring_type = 'standard'

    # Load dist data file
    with open(dist_file) as f:    
        distdata = json.load(f)

    # load prediction file
    with open(pred_file) as f:    
        preddata = {d['player_id']:d for d in json.load(f)}

    # make scorer
    scorer = make_scorer(base_type=scoring_type)

    # score stats
    preddata = {k: score_stats_dict(v, scorer=scorer) for k,v in preddata.iteritems()}

    # add pred data to dist data
    for k, v in distdata.iteritems():
        if k in preddata.keys():
            distdata[k].update({'player_info':preddata[k]})
        else:
            print(k)

    # save updated dist data
    with open(dist_file, 'w') as f:
        json.dump(distdata, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dist_file", type=str,
      help="path of file containing distribution data")
    parser.add_argument("-p", "--pred_file", type=str,
      help="path of file containing prediction data", default='../predictions.json')
    parser.add_argument('-s', '--scoring_type', type=str,
        help='type of scoring: standard, ppr, half_ppr', default='standard')
    args = parser.parse_args()
    main(dist_file=args.dist_file, pred_file=args.pred_file, scoring_type=args.scoring_type)
