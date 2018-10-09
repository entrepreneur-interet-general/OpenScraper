# -*- encoding: utf-8 -*-

from 	tornado.log import enable_pretty_logging, LogFormatter, access_log, app_log, gen_log

gen_log.info("--> importing .settings_scrapy")

from settings_example import *
# from settings import *		# for prod

### settings variables for scrapy



### POLITE WEBSCRAPING
# cf : https://hackernoon.com/how-to-crawl-the-web-politely-with-scrapy-15fbe489573d

# identification 
BOT_NAME		= 	"OpenScraper"
USER_AGENT		= 	"Open Scraper (+https://github.com/entrepreneur-interet-general/OpenScraper)"
					# 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
ROBOTSTXT_OBEY 	= True

'''
check 
wget -U 'Open Scraper (+https://github.com/entrepreneur-interet-general/OpenScraper)' https://fondation.credit-cooperatif.coop/acor 
'''
AUTOTHROTTLE_ENABLED 		= True
HTTPCACHE_ENABLED 			= True

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY 				= .25
RANDOMIZE_DOWNLOAD_DELAY 	= False


# downloaders registration to disable SSL certification
# cf : https://doc.scrapy.org/en/1.0/topics/downloader-middleware.html
# cf : https://stackoverflow.com/questions/32950694/disable-ssl-certificate-verification-in-scrapy
DOWNLOAD_HANDLERS = {
	# 'https': 'scrapy.core.downloader.handlers.http.HttpDownloadHandler', ## --default for https-- 
	'https': 'scraper.downloaders.https.HttpsDownloaderIgnoreCNError',
}

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


