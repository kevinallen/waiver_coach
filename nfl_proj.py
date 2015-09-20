from urllib2 import urlopen
from bs4 import BeautifulSoup

offset = 1
week = 2
while (offset < 300):
    off_url = "http://fantasy.nfl.com/research/projections?offset=" + \
        str(offset) + "&position=O&sort=projectedPts&statCategory=" \
        "projectedStats&statSeason=2015&statType=weekProjectedStats&statWeek=" \
        + str(week)

    soup = BeautifulSoup(urlopen(off_url))

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
        player_stats = [s.span.contents[0] for s in stats]
        stat_labels = ['pass_yds', 'pass_td', 'pass_int', 'rush_yds', 'rush_td',
            'rec_yds','rec_td', 'fum_td', '2pt', 'fum', 'pts']
        print name
        print position
        print opponent
        print player_stats

    break
    offset += 25
