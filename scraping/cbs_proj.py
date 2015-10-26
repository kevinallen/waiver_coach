from urllib2 import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

client = MongoClient()
db = client.data

positions = ['QB','RB','WR','TE','K','DST']
wks = [wk for wk in range(1,17)]

# stats available on CBS
qb_stats = ['pass_attempts','pass_comp', 'pass_yds','pass_tds','int','comp_pct',
    'rush_yds_att','rush_attempts','rush_yds','rush_avg','rush_tds','fumbles',
    'pts']
rb_stats = ['rush_attempts','rush_yds','rush_avg','rush_tds','receptions',
    'rec_yds','rec_avg','rec_tds','fumbles','pts']
wr_te_stats = ['receptions','rec_yds','rec_avg','rec_tds','fumbles','pts']
k_stats = ['fg','fga','xp','pts']
dst_stats = ['int','dfr','ff','sacks','dtd','sty','pa','tyda','pts']

labels = {'QB': qb_stats, 'RB': rb_stats, 'WR': wr_te_stats,
    'TE': wr_te_stats, 'K': k_stats, 'DST': dst_stats}

# these player names are not unique, so the position is used to differentiate
duplicates = {('DAVIDJOHNSON','RB'):'DAVIDJOHNSON',
              ('DAVIDJOHNSON','TE'):'DAVIDJOHNSON1',
              ('RYANGRIFFIN','QB'):'RYANGRIFFIN',
              ('RYANGRIFFIN','TE'):'RYANGRIFFIN1'}

# loop over each position for weeks 1 to 16 of the current season
for wk in wks:
    for pos in positions:
        url = "http://www.cbssports.com/fantasy/football/stats/weeklyprojections/" \
            + pos + "/" + str(wk) + "/avg/ppr?print_rows=9999"
        soup = BeautifulSoup(urlopen(url), "html.parser")

        rows = soup.find('tr',{'class':'label'}).find_next_siblings('tr')

        for row in rows:
            # break loop if we are at the end of the table
            if row.has_attr('class'):
                if 'footer' in row.get('class'):
                    break
            cols = row.find_all('td')

            # create empty variables to hold scraped data
            player_stats = {}
            name = ""
            team = ""

            for i, col in enumerate(cols):
                if i == 0:
                    name = col.a.contents[0]
                    # need to remove &nbsp character and comma
                    team = col.contents[1].split(',')[1].replace(u'\xa0','')
                else:
                    # create dict of projected stats
                    player_stats[labels[pos][i-1]] = col.contents[0]

            # create a key from the player name by removing punctuation and spaces
            name_key = re.sub(r"[\.,\s\']","", name).upper()

            # create new name_key for players with same name
            if (name_key,pos) in duplicates:
                name_key = duplicates[(name_key,pos)]

            player = {'name_key':name_key,'position':pos,'team':team,
                'name':name,'wk':wk, 'source':'cbs'}
            player.update(player_stats)
            # insert player data into mongodb
            db.projections.insert_one(player)
