from urllib2 import urlopen
from bs4 import BeautifulSoup

week = 2
posids = ['10', '20', '30', '40', '80'] # position ids in URL
positions = ['QB', 'RB', 'WR', 'TE', 'K']
# stats are different for each position
qb_stats = ['pass_comp', 'pass_attempts', 'pass_yds', 'pass_td', 'int',
    'rush_attempts', 'rush_yds', 'rush_td', 'pts']
rb_stats = ['rush_attempts', 'rush_yds', 'rush_td', 'receptions',
    'rec_yds', 'rec_td', 'pts']
wr_te_stats = ['receptions', 'rec_yds', 'rec_td', 'pts']
k_stats = ['fg_made', 'fg_miss', 'xp_made', 'xp_miss']
labels = {'QB': qb_stats, 'RB': rb_stats, 'WR': wr_te_stats,
    'TE': wr_te_stats, 'K': k_stats}

for posid in posids:

    urls = ["http://www.fftoday.com/rankings/playerwkproj.php?Season=2015" \
        "&GameWeek=" + str(week) + "&PosID=" + str(posid) + "&LeagueID=1" \
        + "&order_by=FFPts&sort_order=DESC&cur_page=0"]

    # need to page through results for RB and WR
    if posid in ['20','30']:
        urls.append(urls[0].replace('cur_page=0','cur_page=1'))

    for url in urls:
        soup = BeautifulSoup(urlopen(url))

        rows = soup.find('tr',{'class':'tableclmhdr'}).find_next_siblings('tr')

        for row in rows:
            cols = row.find_all('td')

            # store stats and labels in separate lists for each position
            player_stats = []
            name = ""
            team = ""
            opponent = ""
            position = "" # need to get position depending on page visited
            for i, col in enumerate(cols):
                if i == 1:
                    name = col.a.contents[0]
                elif i == 2:
                    team = col.contents[0]
                elif i == 3:
                    opponent = col.contents[0]
                elif i > 3:
                    player_stats.append(col.contents[0])

            print name
            print team
            print opponent
            print labels[positions[posids.index(posid)]]
            print player_stats
