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
