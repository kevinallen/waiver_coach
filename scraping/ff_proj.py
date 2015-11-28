from urllib2 import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

def main(predict_week):
    # storing data in mongodb
    client = MongoClient()
    db = client.data

    # fftoday only shows data for week 1 through the current week
    wks = [wk for wk in range(1,predict_week + 1)]

    posids = ['10', '20', '30', '40', '80'] # position ids in URL
    positions = {'10':'QB', '20':'RB', '30':'WR', '40':'TE', '80':'K'}
    # stats are different for each position
    qb_stats = ['pass_comp', 'pass_attempts', 'pass_yds', 'pass_tds', 'pass_int',
        'rush_attempts', 'rush_yds', 'rush_tds', 'pts']
    rb_stats = ['rush_attempts', 'rush_yds', 'rush_tds', 'receptions',
        'rec_yds', 'rec_tds', 'pts']
    wr_te_stats = ['receptions', 'rec_yds', 'rec_tds', 'pts']
    k_stats = ['fg', 'fg_miss', 'xp', 'xp_miss', 'pts']
    labels = {'QB': qb_stats, 'RB': rb_stats, 'WR': wr_te_stats,
        'TE': wr_te_stats, 'K': k_stats}

    for wk in wks:
        for posid in posids:
            urls = ["http://www.fftoday.com/rankings/playerwkproj.php?Season=2015" \
                "&GameWeek=" + str(wk) + "&PosID=" + str(posid) + "&LeagueID=1" \
                + "&order_by=FFPts&sort_order=DESC&cur_page=0"]

            # need to page through results for RB and WR
            if posid in ['20','30']:
                urls.append(urls[0].replace('cur_page=0','cur_page=1'))

            for url in urls:
                soup = BeautifulSoup(urlopen(url), "html.parser")
                if soup.find('tr',{'class':'tableclmdhr'}) is None:
                    continue

                rows = soup.find('tr',{'class':'tableclmhdr'}).find_next_siblings('tr')

                for row in rows:
                    cols = row.find_all('td')

                    # build player dict
                    player = {}
                    name = ""
                    team = ""
                    opponent = ""

                    for i, col in enumerate(cols):
                        if i == 1:
                            name = col.a.contents[0]
                        elif i == 2:
                            team = col.contents[0]
                        elif i == 3:
                            opponent = col.contents[0]
                        elif i > 3:
                            player[labels[positions[posid]][i-4]] = col.contents[0]

                    # create a key from the player name by removing punctuation and spaces
                    name_key = re.sub(r"[\.,\s\']","", name).upper()

                    player.update({'name':name,'name_key':name_key,
                        'position':positions[posid],'team':team,'source':'FFTODAY',
                        'week':wk, 'year':2015})

                    db.projections.insert_one(player)

if '__name__' == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("week", help="current week of the 2015 season")
    args = parser.parse_args()
    main(predict_week=args.week)
