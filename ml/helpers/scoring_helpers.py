import pandas as pd

# function
def make_scorer(base_type='standard', **kwargs):
    # creates a dictionary of stat:points
    # different base_types (standard, half_ppr, ppr) will set up default values
    # additional values can be specified via kwargs as stat=points
    scores = {
        'receiving_tds':6,
        'receiving_yds':0.1,
        'rushing_tds':6,
        'rushing_yds':0.1
    }
    
    if base_type == 'ppr':
        scores['receiving_rec'] = 1
    elif base_type == 'half_ppr':
        scores['receiving_rec'] = 0.5
    
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            scores[key] = value
    
    return(scores)

# function
def score_stats(stat_df, scorer=make_scorer(base_type='standard')):
    # this takes stat_df, a data frame of statistics, 
    # and a scorer, a dict of stat:points,
    # and returns a series of points
    n = stat_df.shape[0]
    stats = scorer.keys()

    missing_stats = [stat for stat in stats if not stat in stat_df.columns]

    if len(missing_stats) > 0:
        print "stat_df is missing stats defined in scorer, filling with 0: %s" % ', '.join(missing_stats)
        stat_df = pd.concat([stat_df, pd.DataFrame(data={col:[0]*n for col in missing_stats}).set_index(stat_df.index)],axis=1)

    stat_sub = stat_df[stats]
    
    score_df = pd.DataFrame({k:[v]*n for k, v in scorer.iteritems()}).set_index(stat_sub.index)
    return (score_df * stat_sub).sum(axis=1)

