# -*- encoding: utf-8 -*-

from settings_example import *
# from settings import *

### settings variables for scrapy

BOT_NAME		= 	"OpenScraper"
USER_AGENT		= 	"Open Scraper (+https://github.com/entrepreneur-interet-general/OpenScraper)"
					# 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

ITEM_PIPELINES	= 	{ 'scraper.pipelines.MongodbPipeline' : 300 } 

MONGO_URI			= 	MONGODB_APP_URI
MONGO_DATABASE		= 	MONGODB_DB
MONGO_COLL_SCRAP	= 	MONGODB_COLL_DATASCRAPPED

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY 				= .25
RANDOMIZE_DOWNLOAD_DELAY 	= True
