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
        position = player.parent.em.contents[0].split(' - ')[0]
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
        print position
        print opponent
        print player_stats

    offset += 25

# get defensive stats
for offset in [1, 26]:
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
