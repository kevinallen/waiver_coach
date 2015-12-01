from urllib2 import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
import argparse

def main(predict_week):
    # storing data in mongodb
    client = MongoClient()
    db = client.data

    # espn only shows data for week 1 through the current week
    wks = [wk for wk in range(1,predict_week + 1)]

    stat_labels = ['pass_comp', 'pass_attempts', 'pass_yds', 'pass_tds',
        'pass_int', 'rush_attempts', 'rush_yds', 'rush_tds', 'receptions',
        'rec_yds', 'rec_tds', 'pts']

    duplicates = {('DAVIDJOHNSON','RB'):'DAVIDJOHNSON',
                  ('DAVIDJOHNSON','TE'):'DAVIDJOHNSON1'}

    for wk in wks:
        offset = 0
        while offset < 320:
            url = "http://games.espn.go.com/ffl/tools/projections?&scoringPeriodId=" + \
                str(wk) + "&seasonId=2015&startIndex=" + str(offset)

            soup = BeautifulSoup(urlopen(url), "html.parser")

            table = soup.find('table', {'id': 'playertable_0'})
            rows = table.find_all('tr', {'class': lambda x: x and 'pncPlayerRow' in
                x.split()})

            for row in rows:
                player_info = row.find('td', {'class': 'playertablePlayerName'})
                name = player_info.a.contents[0]

                if not 'D/ST' in name:
                    team_info = player_info.contents[1].replace(u'\xa0',u' ')[2:].strip()
                    team_info = team_info.split()
                    team = team_info[0].upper()
                    position = team_info[1]
                else:
                    # TODO: need to map name to team for defense, i.e., Seahawks -> Sea
                    team = ""
                    name = name[:-4]
                    position = "DST"

                # ignore rows that don't have an opponent
                opponent = ""
                try:
                    opponent = player_info.findNext('td').div.a.contents[0]
                except:
                    continue

                stats = row.find_all('td', {'class': lambda x: x and
                    'playertableStat' in x.split()})

                # add all stats to player dict
                player = {}
                for i, stat in enumerate(stats):
                    if i == 0:
                        passing = stat.contents[0].split('/')
                        player[stat_labels[0]] = passing[0] # pass completions
                        player[stat_labels[1]] = passing[1] # pass attempts
                    else:
                        player[stat_labels[i+1]] = stat.contents[0] # all other stats

                # create a key from the player name by removing punctuation and spaces
                name_key = re.sub(r"[\.,\s\']","", name).upper()

                # create new name_key for players with same name
                if (name_key,position) in duplicates:
                    name_key = duplicates[(name_key,position)]

                # add rest of fields to player dict
                player.update({'name':name,'position':position,'team':team,'week':wk,
                    'year':2015,'source':'ESPN','name_key':name_key})

                # add player to db
                db.projections.insert_one(player)

            offset += 40
            # go to the next week

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("week", type=int, help="current week of the 2015 season")
    args = parser.parse_args()
    main(predict_week=args.week)
