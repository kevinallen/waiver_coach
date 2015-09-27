from urllib2 import urlopen
from bs4 import BeautifulSoup

offset = 1
week = 2

# get offensive stats
while (offset < 300):
    url = "http://fantasy.nfl.com/research/projections?offset=" + \
        str(offset) + "&position=O&sort=projectedPts&statCategory=" \
        "projectedStats&statSeason=2015&statType=weekProjectedStats&statWeek=" \
        + str(week)

    soup = BeautifulSoup(urlopen(url))

    table = soup.find('table', {'class': lambda x: x and 'tableType-player'})
    rows = table.tbody.find_all("tr")

    for row in rows:
        player = row.find('a', {'class': lambda x: x and 'playerNameFull'
            in x.split()})

        name = player.contents[0]
        team_info = player.parent.em.contents[0].split(' - ')
        position = team_info[0]
         # if player is dropped, they won't have a team listed
        if len(team_info) > 1:
            team = team_info[1]
        else:
            team = "dropped"
        opp = row.find('td', {'class': 'playerOpponent'})
        opponent = opp.contents[0]

        stats = opp.find_next_siblings('td')
        player_stats = []
        for stat in stats:
            if stat.span:
                player_stats.append(stat.span.contents[0])
            else:
                player_stats.append(stat.contents[0])

        stat_labels = ['pass_yds', 'pass_td', 'pass_int', 'rush_yds', 'rush_td',
            'rec_yds','rec_td', 'fum_td', '2pt', 'fum', 'pts']
        print name
        print team
        print position
        print opponent
        print player_stats

    offset += 25

# get defense and kicker stats
for offset in [1, 26]:
    # defense
    url = "http://fantasy.nfl.com/research/projections?offset=" + \
        str(offset) + "&position=8&sort=projectedPts&statCategory=" \
        "projectedStats&statSeason=2015&statType=weekProjectedStats&statWeek=" \
        + str(week)

    soup = BeautifulSoup(urlopen(url))
    table = soup.find('table', {'class': lambda x: x and 'tableType-player'})
    rows = table.tbody.find_all("tr")

    for row in rows:
        player = row.find('a', {'class': lambda x: x and 'playerNameFull'
            in x.split()})

        name = player.contents[0]
        opp = row.find('td', {'class': 'playerOpponent'})
        opponent = opp.contents[0]
        stats = opp.find_next_siblings('td')
        player_stats = [s.span.contents[0] for s in stats]
        stat_labels = ['sack', 'int', 'fum_rec', 'safety', 'td', 'ret_td',
            'pts_allow', 'pts']
        print name
        print opponent
        print player_stats

    # kicker
    url = "http://fantasy.nfl.com/research/projections?offset=" + \
        str(offset) + "&position=7&sort=projectedPts&statCategory=" \
        "projectedStats&statSeason=2015&statType=weekProjectedStats&statWeek=" \
        + str(week)

    soup = BeautifulSoup(urlopen(url))
    table = soup.find('table', {'class': lambda x: x and 'tableType-player'})
    rows = table.tbody.find_all("tr")

    for row in rows:
        player = row.find('a', {'class': lambda x: x and 'playerNameFull'
            in x.split()})

        name = player.contents[0]
        opp = row.find('td', {'class': 'playerOpponent'})
        opponent = opp.contents[0]
        stats = opp.find_next_siblings('td')

        # some player stats are missing, so need to check for span tag
        player_stats = []
        for stat in stats:
            if stat.span:
                player_stats.append(stat.span.contents[0])
            else:
                player_stats.append(stat.contents[0])
        stat_labels = ['pat_made', 'fg_made_0-19', 'fg_made_20-29',
            'fg_made_30-39', 'fg_made_40-49', 'fg_made_50', 'pts']
        print name
        print opponent
        print stat_labels
        print player_stats
