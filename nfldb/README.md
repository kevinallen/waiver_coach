# Getting nfldb up and running

# Install postgrs

following instructions for a Mac here: http://www.russbrooks.com/2010/11/25/install-postgresql-9-on-os-x
	
	brew rm postgresql --force
	brew update
	brew install postgresql

Follow the instructions that postgres gives after install, for me it was:
	
	ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents
	launchctl load ~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist

The first command above makes postgres start on log in
The second command makes postgres start now
To check that this works:
	
	createdb mydb

You should get no response. Then:
	
	dropdb mydb

# Create empty nfldb

Now I'm going to try following the instructions on the nfldb installation guide: https://github.com/BurntSushi/nfldb/wiki/Installation

This first command creates the an nfldb role, you will have to enter a password twice.

	createuser -U rossboberg -E -P nfldb

Note that rossboberg is the username I installed under. Now, create the DB under the new nfldb user.

	createdb -U rossboberg -O nfldb nfldb

And enable fuzzystrmatch for fuzzy player searching:

	psql -U rossboberg -c 'CREATE EXTENSION fuzzystrmatch;' nfldb

You should now be able to log in and connect to nfldb

	psql -U nfldb nfldb

# Installing the nfldb database

Following the instructions from here: https://github.com/BurntSushi/nfldb/wiki/Installation#importing-the-nfldb-database

Download and unzip the suggested zip file. I am going to save it in a folder called waiver_coach_data, that sits in the same directory as our git repo, waiver_coach. It's too big to be pushed to git (~250mb).

	ROSSs-MacBook-Pro:capstone rossboberg$ ls
	waiver_coach		waiver_coach_data

Then load the downloaded file (nfldb.sql) in to postgres
	
	psql -U nfldb nfldb < nfldb.sql

This failed because I used rossboberg instead of postgres above. Trying to fix retrospectively. Start postgres as rossboberg (superuser)

	psql -U rossboberg nfldb

Then create postgres super user from the psql command line:

	CREATE USER postgres SUPERUSER;
	\q

Then delete nfldb database and recreate it as postgres

	dropdb nfldb
	createdb -U postgres -O nfldb nfldb
	psql -U postgres -c 'CREATE EXTENSION fuzzystrmatch;' nfldb

And try again

	psql -U nfldb nfldb < nfldb.sql

Make sure it worked

	ROSSs-MacBook-Pro:waiver_coach_data rossboberg$ psql -U nfldb nfldb
	psql (9.4.4)
	Type "help" for help.

	nfldb=> d
	nfldb-> \d
	          List of relations
	 Schema |    Name     | Type  | Owner 
	--------+-------------+-------+-------
	 public | agg_play    | table | nfldb
	 public | drive       | table | nfldb
	 public | game        | table | nfldb
	 public | meta        | table | nfldb
	 public | play        | table | nfldb
	 public | play_player | table | nfldb
	 public | player      | table | nfldb
	 public | team        | table | nfldb


# Installing the nfldb Python module

Still following this: https://github.com/BurntSushi/nfldb/wiki/Installation#installing-the-nfldb-python-module

	pip2 install nfldb

## Confliguring nfldb

We need to tell nfldb how to connet to the database we created. We need to find the configuration file that was installed with nfldb. On my mac it was in:

	/usr/local/share/nfldb/config.ini.sample

Make a folder called nfldb in you local .config file

	mkdir -p $HOME/.config/nfldb
	cp /usr/local/share/nfldb/config.ini.sample $HOME/.config/nfldb/config.ini

Change values in config.ini. I changed the timezone and the password as entered earlier.

# Test it out

Create the following called top-ten-qbs.py

	import nfldb

	db = nfldb.connect()
	q = nfldb.Query(db)

	q.game(season_year=2012, season_type='Regular')
	for pp in q.sort('passing_yds').limit(10).as_aggregate():
	    print pp.player, pp.passing_yds

And it works!

	ROSSs-MacBook-Pro:nfldb rossboberg$ python top-ten-qbs.py 
	Drew Brees (NO, QB) 5177
	Matthew Stafford (DET, QB) 4965
	Tony Romo (DAL, QB) 4903
	Tom Brady (NE, QB) 4799
	Matt Ryan (ATL, QB) 4719
	Peyton Manning (DEN, QB) 4667
	Andrew Luck (IND, QB) 4374
	Aaron Rodgers (GB, QB) 4303
	Josh Freeman (UNK, UNK) 4065
	Carson Palmer (ARI, QB) 4018