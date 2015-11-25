# web_helpers.py
Contains a function that returns a dataframe of predicted data scraped from the web.

# Need MongoDB for these

## Instaling MongoDB
You can follow instructions here to install mongo on a Mac: http://www.mongodbspain.com/en/2014/11/06/install-mongodb-on-mac-os-x-yosemite/

## Loading Data
You will also need to load the vegas data. Kevin saved a file called vegas.csv in the scraping folder of this repo:

	/scraping/vegas.csv

The code assumes you have the vegas data in a database called `data` and a collection called `vegas`. You can load the file with this command:

	mongoimport --host=127.0.0.1 -d data -c vegas --type csv --file vegas.csv --headerline

Note that I needed the `--host=127.0.0.1` option, but Kevin did not.