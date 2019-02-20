# -*- encoding: utf-8 -*-

print( "---------- IMPORT SETTINGS_SCRAPYS.PY -------- " )

from tornado.options import options

from 	tornado.log import enable_pretty_logging, LogFormatter, access_log, app_log, gen_log
gen_log.info("--> importing .settings_scrapy")

import os

### to get MONGODB_APP_URI, etc...
### for debugging purposes
print "current port from options : ", options.port 
print "current mode from options : ", options.mode 

if options.mode == "default" :
	from settings_example import *
if options.mode == "production" :
	from settings_secret import *

# from settings import *		# for prod

# ### GET APP MODE FROM ENV VARS
# APP_MODE = os.environ.get('APP_MODE', 'default')
# gen_log.debug("--> APP_MODE : %s", APP_MODE)





### settings variables for scrapy


### POLITE WEBSCRAPING
# cf : https://hackernoon.com/how-to-crawl-the-web-politely-with-scrapy-15fbe489573d

# identification 
BOT_NAME		= 	"OpenScraper"
USER_AGENT		= 	"Open Scraper (+https://github.com/entrepreneur-interet-general/OpenScraper)"
					# 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
ROBOTSTXT_OBEY 	= False

CHROME_HEADLESS = True

'''
check 
wget -U 'Open Scraper (+https://github.com/entrepreneur-interet-general/OpenScraper)' https://fondation.credit-cooperatif.coop/acor 
'''
AUTOTHROTTLE_ENABLED 		= True
HTTPCACHE_ENABLED 			= True

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# RETRY_TIMES					= 5
# DOWNLOAD_DELAY 				= .7
RANDOMIZE_DOWNLOAD_DELAY 	= False
JOBDIR_FOLDER 				= "running_spiders"

# CONCURRENT_ITEMS				= 200
# CONCURRENT_REQUESTS			= 100
CONCURRENT_REQUESTS_PER_DOMAIN 	= 8
REDIRECT_MAX_TIMES				= 20

DOWNLOAD_MAXSIZE		= 0 
DEPTH_PRIORITY 			= 1
SCHEDULER_DISK_QUEUE 	= 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE 	= 'scrapy.squeue.FifoMemoryQueue'


# downloaders registration to disable SSL certification
# cf : https://doc.scrapy.org/en/1.0/topics/downloader-middleware.html
# cf : https://stackoverflow.com/questions/32950694/disable-ssl-certificate-verification-in-scrapy
# DOWNLOAD_HANDLERS = {
# 	# 'https': 'scrapy.core.downloader.handlers.http.HttpDownloadHandler', ## --default for https-- 
# 	'https': 'scraper.downloaders.https.HttpsDownloaderIgnoreCNError',
# }

# pipelines registration
ITEM_PIPELINES	= 	{ 
	'scraper.pipelines.MongodbPipeline' : 300 
} 


# database for items - can be the same as server but can be different too
# imported from settings_example.py for demo or settings for prod
DB_DATA_URI			= 	MONGODB_APP_URI
DB_DATA_DATABASE	= 	MONGODB_DB
DB_DATA_COLL_SCRAP	= 	MONGODB_COLL_DATASCRAPPED


# default values for runner
DEFAULT_COUNTDOWN = 3 	# countdown in seconds before running generic spider


# possible chromedriver path
CHROMEDRIVER_PATH_LIST = {
	'default' 		: '/usr/local/bin/chromedriver',			# in mac
	'production' 	: '/usr/lib/chromium-browser/chromedriver',	# in Ubuntu 
}

