from urllib2 import urlopen
from bs4 import BeautifulSoup

week = 2
offset = 0 # shows 40 at a time

while offset < 320:
    url = "http://games.espn.go.com/ffl/tools/projections?&scoringPeriodId=" + \
        str(week) + "&seasonId=2015&startIndex=" + str(offset)

    soup = BeautifulSoup(urlopen(url))

    table = soup.find('table', {'id': 'playertable_0'})
    rows = table.find_all('tr', {'class': lambda x: x and 'pncPlayerRow' in
        x.split()})

    for row in rows:
        player_info = row.find('td', {'class': 'playertablePlayerName'})
        name = player_info.a.contents[0]

        if not 'D/ST' in name:
            team_info = player_info.contents[1].replace(u'\xa0',u' ')[2:].strip()
            team_info = team_info.split()
            team = team_info[0]
            position = team_info[1]
        else:
            team = ""
            position = "DEF"

        opponent = player_info.findNext('td').div.a.contents[0]
        stats = row.find_all('td', {'class': lambda x: x and
            'playertableStat' in x.split()})
        player_stats = []
        for i, stat in enumerate(stats):
            if i == 0:
                passing = stat.contents[0].split('/')
                player_stats.append(passing[0])
                player_stats.append(passing[1])
            else:
                player_stats.append(stat.contents[0])
        stat_labels = ['pass_comp', 'pass_attempts', 'pass_yds', 'pass_td',
            'pass_int', 'rush_attempts', 'rush_yds', 'rush_td', 'receptions',
            'rec_yds', 'rec_td', 'pts']

        print name
        print team
        print position
        print opponent
        print player_stats

    offset += 40
