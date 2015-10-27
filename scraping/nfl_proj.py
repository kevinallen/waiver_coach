from urllib2 import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

# storing data in mongodb
client = MongoClient()
db = client.data

wks = [wk for wk in range(1,17)]

for wk in wks:
    offset = 1
    while (offset < 300):
        # position players
        stat_labels = ['pass_yds', 'pass_tds', 'pass_int', 'rush_yds', 'rush_tds',
            'rec_yds','rec_tds', 'fum_td', '2pt', 'fumbles', 'pts']

        url = "http://fantasy.nfl.com/research/projections?offset=" + \
            str(offset) + "&position=O&sort=projectedPts&statCategory=" \
            "projectedStats&statSeason=2015&statType=weekProjectedStats&statWeek=" \
            + str(wk)

        soup = BeautifulSoup(urlopen(url), "html.parser")

        table = soup.find('table', {'class': lambda x: x and 'tableType-player'})
        rows = table.tbody.find_all("tr")

        for row in rows:
            player_info = row.find('a', {'class': lambda x: x and 'playerNameFull'
                in x.split()})

            name = player_info.contents[0]
            team_info = player_info.parent.em.contents[0].split(' - ')
            position = team_info[0]
             # if player is dropped, they won't have a team listed
            if len(team_info) > 1:
                team = team_info[1]
            else:
                team = ""
            opp = row.find('td', {'class': 'playerOpponent'})
            opponent = opp.contents[0]
            cols = opp.find_next_siblings('td')

            # some player stats are missing, so need to check for span tag
            player = {}
            for i,col in enumerate(cols):
                if col.span:
                    player[stat_labels[i]] = col.span.contents[0]
                else:
                    player[stat_labels[i]] = col.contents[0]

            # create a key from the player name by removing punctuation and spaces
            name_key = re.sub(r"[\.,\s\']","", name).upper()

            player.update({'name':name,'name_key':name_key,'position':position,
                'team':team,'week':wk,'year':2015,'source':'NFL'})

            db.projections.insert_one(player)

        offset += 25


    # get defense and kicker stats
    for offset in [1, 26]:
        # defense
        stat_labels = ['sacks', 'int', 'fum_rec', 'sty', 'td', 'ret_td',
            'pts_allow', 'pts']

        url = "http://fantasy.nfl.com/research/projections?offset=" + \
            str(offset) + "&position=8&sort=projectedPts&statCategory=" \
            "projectedStats&statSeason=2015&statType=weekProjectedStats&statWeek=" \
            + str(wk)

        soup = BeautifulSoup(urlopen(url), "html.parser")
        table = soup.find('table', {'class': lambda x: x and 'tableType-player'})
        rows = table.tbody.find_all("tr")

        for row in rows:
            player_info = row.find('a', {'class': lambda x: x and 'playerNameFull'
                in x.split()})

            name = player_info.contents[0]
            opp = row.find('td', {'class': 'playerOpponent'})
            opponent = opp.contents[0]
            cols = opp.find_next_siblings('td')
            player_stats = [col.span.contents[0] for col in cols]

            # build player dict
            player = {}
            for i,stat in enumerate(player_stats):
                player[stat_labels[i]] = stat

            # create a key from the player name by removing punctuation and spaces
            name_key = re.sub(r"[\.,\s\']","", name).upper()

            player.update({'name':name,'name_key':name_key,'team':"",
                'position':'DST','week':wk, 'year':2015, 'source':'NFL'})

            db.projections.insert_one(player)

        # kicker
        stat_labels = ['pat_made', 'fg_made_0-19', 'fg_made_20-29',
            'fg_made_30-39', 'fg_made_40-49', 'fg_made_50', 'pts']

        url = "http://fantasy.nfl.com/research/projections?offset=" + \
            str(offset) + "&position=7&sort=projectedPts&statCategory=" \
            "projectedStats&statSeason=2015&statType=weekProjectedStats&statWeek=" \
            + str(wk)

        soup = BeautifulSoup(urlopen(url), "html.parser")
        table = soup.find('table', {'class': lambda x: x and 'tableType-player'})
        rows = table.tbody.find_all("tr")

        for row in rows:
            player_info = row.find('a', {'class': lambda x: x and 'playerNameFull'
                in x.split()})

            name = player_info.contents[0]
            team_info = player_info.parent.em.contents[0].split(' - ')
            position = team_info[0]
             # if player is dropped, they won't have a team listed
            if len(team_info) > 1:
                team = team_info[1]
            else:
                team = ""
            opp = row.find('td', {'class': 'playerOpponent'})
            opponent = opp.contents[0]
            cols = opp.find_next_siblings('td')

            # build player dict
            player = {}
            for i,col in enumerate(cols):
                if col.span:
                    player[stat_labels[i]] = col.span.contents[0]
                else:
                    player[stat_labels[i]] = col.contents[0]

            # create a key from the player name by removing punctuation and spaces
            name_key = re.sub(r"[\.,\s\']","", name).upper()

            player.update({'name':name,'name_key':name_key,'team':team,
                'position':position,'week':wk, 'year':2015, 'source':'NFL'})

            db.projections.insert_one(player)
