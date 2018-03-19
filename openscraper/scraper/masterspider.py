# -*- encoding: utf-8 -*-

import 	pprint
import 	os 

import 	time
from 	datetime import datetime

# cf : http://blog.jmoz.co.uk/python-convert-datetime-to-timestamp/
""" # snippet datetime and timestamp
	import datetime
	readable = datetime.datetime.fromtimestamp(1520437834).isoformat()
	print(readable)
	# 2018-03-07T16:50:34+01:00
"""

### import app settings
from config.settings_example import * 
# from config.settings import * 
from config.settings_scrapy import * 


### logging only for scrapy
from 	os import path, remove
import 	logging
import 	logging.config
from 	logging.config import dictConfig
from 	config.settings_logging import logging_config

### lOGGER - SCRAPY

# set logger for scrapy
log_scrap = logging.getLogger("log_scraper")
log_scrap.setLevel(logging.DEBUG)

# Create the Handler for logging data to a file
logger_handler = logging.FileHandler('logs/openscraper_scrapy_logging.log')
logger_handler.setLevel(logging.WARNING)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
log_scrap.addHandler(logger_handler)
log_scrap.info('>>> Completed configuring log_scraper !')



### import scrapy utilities
import scrapy

from multiprocessing 		import Process, Queue
from twisted.internet 		import reactor, defer

from scrapy.utils.log 		import configure_logging
from scrapy.utils.project 	import get_project_settings

from scrapy.settings 		import Settings

from scrapy 				import Spider
from scrapy.crawler 		import CrawlerProcess, CrawlerRunner
# from scrapy.spiders 	import SitemapSpider, CrawlSpider
# import scrapy.crawler as 	   crawler



### settings scrapy

# s = get_project_settings()
# print "\ndefault settings scrapy : "
# pprint.pprint(dict(s))
# update settings from settings_scrapy.py
# s.update(dict(ITEM_PIPELINES={
# 	'openscraper.pipelines.RestExportPipeline': 300,
# }))
# print "\nupdated settings scrapy : "
# pprint.pprint(dict(s))


### SCRAPY PIPELINES....
# update setting to use the pipeline which will write results (items) in the database or files
# cf self-contained scrapy : https://gist.github.com/alecxe/fc1527d6d9492b59c610
# cf self-contained scrapy : https://github.com/kirankoduru/scrapy-programmatically/

### set scrapy from settings_scrapy.py
settings = Settings()

settings.set( "BOT_NAME"					, BOT_NAME )
settings.set( "USER_AGENT"					, USER_AGENT )
# settings.set( "ROBOTSTXT_OBEY"				, ROBOTSTXT_OBEY )

settings.set( "ITEM_PIPELINES"				, ITEM_PIPELINES )

settings.set( "DB_DATA_URI" 				, DB_DATA_URI )
settings.set( "DB_DATA_DATABASE" 			, DB_DATA_DATABASE )
settings.set( "DB_DATA_COLL_SCRAP" 			, DB_DATA_COLL_SCRAP )


print "\n>>> settings scrapy : "
pprint.pprint(dict(settings))

print "\n"
print "--- run_generic_spider / BOT_NAME : "	
print settings.get('BOT_NAME')
print "--- run_generic_spider / USER_AGENT : "	
print settings.get('USER_AGENT')
print "--- run_generic_spider / ITEM_PIPELINES : " 	
print settings.get('ITEM_PIPELINES').__dict__




### import base_fields ###############
### import main args fom config.settings_corefields.py
from config.settings_corefields import * # mainly for DATAMODEL_CORE_FIELDS_ITEM

### import items
from items import * # GenericItem #, StackItem #ScrapedItem

### import mixins
# from mixins import GenericSpiderMixin

### define pipelines



#####################################################
"""
	error_array = []
	item_count = 0  # will be incremented each time a new item is created
	item_count_depth_1 = 0  # will be incremented each time an item is completed in detailed page
	LIMIT = 5  # The number of pages where the spider will stop
	page_count = 1  # The number of pages already scraped
	name = ""  # The name of the spider to use when executing the spider
	download_delay = 0  # The delay in seconds between each request. some website will block too many requests
	page_url = ""  # base url (ex : "https://www.mysite.org")
	label = ""
	start_urls = []  # List of URLs that will be crawled by the parse method
"""


#####################################################
### define generic spider
### cf : https://blog.scrapinghub.com/2016/02/24/scrapy-tips-from-the-pros-february-2016-edition/

# process = crawler.CrawlerRunner()


### UTILS FOR SPIDERS

# to be used in run_generic_spider function
def flattenSpiderConfig(run_spider_config) :
	"""creates a flat dict from nested spider_config dict"""
	spider_config_flat = {}
	for conf_class, conf_set in run_spider_config.iteritems() :
		if conf_class != "_id" :
			for conf_field, conf_data in conf_set.iteritems() : 
				spider_config_flat[conf_field] = conf_data
	return spider_config_flat


# to be used in GenericSpider class
'''
def dictFromDataModelList (datamodel_list ) : 
	"""creates a correspondance dict from datamodel to _xpath """
	
	# data_model_dict = { i : "{}_xpath".format(i) for i in datamodel_list }
	
	data_model_dict = { str(i["_id"]) : i for i in datamodel_list }
	
	return data_model_dict
'''



### ON ITEMS AND PIPELINES SEE : https://gist.github.com/alecxe/fc1527d6d9492b59c610



class GenericSpider(Spider) :
	
	"""a generic spider to be configured with datamodel and spider_config_flat variables"""
	
	### spider class needs a default name
	name = "genericspider"

	def __init__(self, user_id=None, datamodel=None, spider_id=None, spider_config_flat=None, *args, **kwargs) : 
		
		### super init/override spider class with current args 
		# print "\n--- GenericSpider / __init__ :"
		log_scrap.info("--- GenericSpider / __init__ :")

		super(GenericSpider, self).__init__(*args, **kwargs)
		
		self.user_id	= user_id
		self.spider_id 	= spider_id

		### store spider_config_flat
		print "\n--- GenericSpider / spider_config_flat :"
		pprint.pprint(spider_config_flat)
		self.spider_config_flat = spider_config_flat

		### getting all the config args from spider_config_flat (i.e. next_page, ...)
		print "\n--- GenericSpider / passing kwargs..."
		for k, v in spider_config_flat.iteritems() : 
			print "   - ", k, ":", v
			self.__dict__[k] = v


		### getting data model for later use in item
		print "\n--- GenericSpider / datamodel :"
		# self.datamodel = datamodel 
		pprint.pprint (datamodel[:3])
		print "..."

		### storing correspondance dict from datamodel
		self.dm_core 					= { i["field_name"] : { "field_type" : i["field_type"] } for i in datamodel if i["field_class"] == "core" }
		self.dm_core_item_related 		= DATAMODEL_CORE_FIELDS_ITEM
		# self.dm_core_item_related_dict	= DATAMODEL_CORE_FIELDS_ITEM
		self.dm_custom 					= { str(i["_id"]) 	: { "field_type" : i["field_type"] } for i in datamodel if i["field_class"] == "custom" }
		self.dm_custom_list 			= self.dm_custom.keys()

		print "\n--- GenericSpider / dm_item_related :"
		self.dm_item_related 			= self.dm_custom_list + self.dm_core_item_related
		pprint.pprint(self.dm_item_related)

	'''
	def parse(self, response):
		"""
		parse pages to scrap data
		"""
		for scraped_data in response.css('div.quote'):
			
			### create Item to fill
			# item = ScrapedItem()
			item = self.custom_item
			
			### TO DO : fill item with results
			# self.fill_item_from_results_page(action, item)

			print(scraped_data.css('span.text::text').extract_first())

		is_next_page, next_page = self.get_next_page(response)
		if is_next_page:
			yield response.follow(next_page, callback=self.parse)

	def get_next_page(self, response, no_page_url):
		has_next_page = True
		has_not_next_page = False
	'''

	def parse(self, response):
		"""
		parse pages to scrap data
		"""

		print "--- GenericSpider.parse ..."

		print response.xpath(self.item_xpath)[0]

		### loop through data items in page in response
		for raw_data in response.xpath(self.item_xpath):
			
			### instantiate Item to fill from datamodel
			itemclass 	= create_item_class( 'GenericItemClass', fields_list = self.dm_item_related )
			item 		= itemclass()
			
			# just for debugging purposes
			# item[ 'testClass' ]	= "item class is tested"

			# add global info to item : i.e. core fields in dm_core_item_related list
			item[ 'spider_id' ]	= self.spider_id
			item[ 'added_by'  ]	= self.user_id 
			item[ 'added_at'  ]	= time.time()		# timestamp
			# TO DO : store urls for this item
			item[ 'link_data']	= ""
			item[ 'link_src' ]	= ""

			### extract data and feed it to Item instance based on spider_config_flat
			for d_model in self.dm_custom_list : 

				### first, checks if xpath exists in spider_config_flat
				if d_model in self.spider_config_flat : 
					
					### check if field is not empty
					if self.spider_config_flat[ d_model ] != [] and self.spider_config_flat[ d_model ] != "" :
						
						### fill item field corresponding to xpath
						item[ d_model ] = raw_data.xpath(self.spider_config_flat[ d_model ]).extract()


			### item completion is finished - yield and so spark pipeline for item (store in db for instance)
			# print "\nGenericSpider.parse - item : \n", item.items()
			# print item.keys()
			yield item

			### if need to follow to extract all data
			if self.spider_config_flat["parse_follow"] == True : 
				url = item['link']
				yield scrapy.Request(url, callback=self.parse_detailed_page, meta={'item': item})


		### get and go to next page 
		# next_page_url = response.xpath(self.spider_config_flat[ "next_page_xpath" ]).extract_first()
		# if next_page_url is not None:
		# 	print "\n --- GenericSpider.parse / NEXT PAGE... \n"
		# 	# yield scrapy.Request(response.urljoin(next_page_url))
		# 	yield scrapy.follow(response.urljoin(next_page_url, callback=self.parse))

		is_next_page, next_page = self.get_next_page(response)
		if is_next_page:
			print "\n --- GenericSpider.parse / NEXT PAGE... \n"
			yield response.follow(next_page, callback=self.parse)


	### TO DO : good follow up and callbacks
	def get_next_page(self, response):
		"""tries to find a new page to scrap.
		if it finds one, returns it along with a True value"""
		next_page = response.xpath(self.next_page).extract_first()
		if (next_page is not None) and (self.page_count < self.LIMIT):
			self.page_count += 1
			# next_page = next_page.strip()
			# next_page = self.add_string_to_complete_url_if_needed(next_page, self.page_url)
			next_page = response.xpath(self.spider_config_flat[ "next_page" ]).extract_first()
			return True, next_page
		else:
			return False, next_page

	def add_string_to_complete_url_if_needed(self, not_complete_url, rest_of_url=None):
		"""adds the missing beggining part of an url with the '/' if needed"""
		if rest_of_url is None:
			rest_of_url = self.page_url
		if not not_complete_url.startswith("http"):
			if not not_complete_url.startswith("/"):
				not_complete_url = "{}{}".format("/", not_complete_url)
			not_complete_url = "{}{}".format(rest_of_url, not_complete_url)
		return not_complete_url

	def parse_item (self, response): 

		### create Item to fill
		itemclass = create_item_class('GenericItemClass', self.datamodel)
		item = itemclass()

		### just for debugging purposes
		item['testClass'] = "class is tested"

		### extract data and feed it to item based on spider_config_flat
		for d_model, d_xpath in self.datamodel_dict.iteritems() : 
			# first, checks if xpath exists in spider_config_flat
			if d_xpath in self.spider_config_flat : 
				# fill item field corresponding to xpath
				item[ d_model ] = raw_data.xpath(self.spider_config_flat[ d_xpath ]).extract()

		print "\nGenericSpider.parse - item : \n", item.items()
		# print item.keys()
		yield item



	### TO DO : generic functions linked with DATAMODEL_FIELDS_TYPES
	def get_type_text(self, response) :
		"""
		for field_type : "text"
		"""
		value = ""
		return value

	def get_type_tags(self, response) :
		"""
		for field_type : "tags"
		"""
		value = ""
		return value

	def get_type_url(self, response) :
		"""
		for field_type : "url", "email"
		"""
		value = ""
		return value

	def get_type_adress(self, response) : 
		"""
		for field_type : "adress"
		"""
		value = ""
		return value

	def get_type_image(self, response) : 
		"""
		fields : "image"
		"""
		value = ""
		return value

	def get_type_date(self, response) : 
		"""
		for field_type : "date"
		"""
		value = ""
		return value



### define the spider runner
### cf : https://stackoverflow.com/questions/13437402/how-to-run-scrapy-from-within-a-python-script
### cf : https://doc.scrapy.org/en/latest/topics/practices.html
### solution chosen from : https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable 

def run_generic_spider( user_id				= None, 
						spider_id			= None, 
						datamodel			= None, 
						run_spider_config	= None 
						):
	"""
	just launch run_generic_spider() from any handler in controller
	"""

	print "\n--- run_generic_spider / spider_id : ", spider_id
	
	# !!! spider is launched from main.py level !!! 
	# all relative routes referring to this...
	print "\n--- run_generic_spider / os.getcwd() : ", os.getcwd() 

	### flattening run_spider_config : from nested to flat dict 
	# print "--- run_generic_spider / run_spider_config : "
	# pprint.pprint(run_spider_config)
	print "--- run_generic_spider / flattening run_spider_config --> spider_config_flat"
	spider_config_flat = flattenSpiderConfig( run_spider_config )
	# print "--- run_generic_spider / spider_config_flat : "
	# pprint.pprint(spider_config_flat)

	### settings for crawler
	# cf : https://hackernoon.com/how-to-crawl-the-web-politely-with-scrapy-15fbe489573d
	# gllobal settings for scrapy processes (see upper)
	print "--- run_generic_spider / BOT_NAME :       ", settings.get('BOT_NAME')
	print "--- run_generic_spider / USER_AGENT :     ", settings.get('USER_AGENT')
	print "--- run_generic_spider / ITEM_PIPELINES : ", settings.get('ITEM_PIPELINES').__dict__
	# specific settings for this scrapy process
	settings.set( "CURRENT_SPIDER_ID" 				, spider_id )
	settings.set( "DOWNLOAD_DELAY" 					, DOWNLOAD_DELAY )
	settings.set( "RANDOMIZE_DOWNLOAD_DELAY"		, RANDOMIZE_DOWNLOAD_DELAY )

	### initiating crawler process
	print "\n--- run_generic_spider / instanciate process ..." 	
	# process = CrawlerRunner() 
	# process = CrawlerProcess()
	process = CrawlerRunner( settings = settings )

	### adding CrawlerRunner as deferred
	def f(q):
		try:
			### send/create custom spider from run_spider_config
			### cf : https://stackoverflow.com/questions/35662146/dynamic-spider-generation-with-scrapy-subclass-init-error
			
			deferred = process.crawl( GenericSpider, 
										user_id				= user_id,
										datamodel 			= datamodel , 
										spider_id 			= spider_id ,
										spider_config_flat	= spider_config_flat 
									)			
			deferred.addBoth(lambda _: reactor.stop())
			reactor.run()
			q.put(None)
		except Exception as e:
			q.put(e)

	### putting task in queue and start
	q = Queue() 
	p = Process(target=f, args=(q,))
	p.start()
	result = q.get()
	p.join()

	if result is not None:
		raise result






#############################################
### cool snippets 

	### convert to class object
	# spider = globals()[spider]