# Web Scraping
The Python scripts in this directory scrape data from the web to supplement the data in nfldb.

### Projected Stats
The following files scrape projected stats. Prior to running these scripts, it is necessary to install and run MongoDB locally (see below).

 - cbs_proj.py
 - espn_proj.py
 - ff_proj.py
 - nfl_proj.py

### Install MongoDB with Homebrew

[Install MongoDB on OS X](https://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/)

```Shell
brew update
brew install mongodb
# create the default data directory
mkdir -p /data/db
# start the db
mongod
```

This will start MongoDB on the default port.

### Get projections
If you have previously added these projections to MongoDB, you will need to delete that data. Execute the following commands from the Mongo CLI.

```
use data
db.projections.remove({})
```

Then run the python scripts from the terminal. For example, to get data for week 12:

```Shell
python scraping/espn_proj.py 12 \
&& python scraping/ff_proj.py 12 \
&& python scraping/nfl_proj.py \
&& python scraping/cbs_proj.py
```
