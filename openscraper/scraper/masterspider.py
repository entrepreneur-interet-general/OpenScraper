# -*- encoding: utf-8 -*-

from 	tornado.log import enable_pretty_logging, LogFormatter, access_log, app_log, gen_log

gen_log.info("--> importing .masterspider")


# import 	pprint
from 	pprint import pprint, pformat
import 	os 
import 	re
import 	time
from 	datetime import datetime
import 	json


# cf : http://blog.jmoz.co.uk/python-convert-datetime-to-timestamp/
""" # snippet datetime and timestamp
	import datetime
	readable = datetime.datetime.fromtimestamp(1520437834).isoformat()
	print(readable)
	# 2018-03-07T16:50:34+01:00
"""

### import app settings
from config.settings_example import * 
# from config.settings import *  		# for prod

from config.settings_scrapy import * 
from config.settings_cleaning import *

### lOGGER - SCRAPY
### logging only for scrapy
from 	os import path, remove
import 	logging
import 	logging.config
from 	logging.config import dictConfig
from 	config.settings_logging import logging_config

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
log_scrap.debug('>>> Completed configuring log_scraper !')



### import scrapy utilities
import scrapy

from multiprocessing 		import Process, Queue
from twisted.internet 		import reactor, defer

from scrapy.http 			import Request

from scrapy.utils.log 		import configure_logging
from scrapy.utils.project 	import get_project_settings

from scrapy.settings 		import Settings

from scrapy 				import Spider
from scrapy.crawler 		import CrawlerProcess, CrawlerRunner
from scrapy.exceptions		import CloseSpider
# from scrapy.spiders 	import SitemapSpider, CrawlSpider
# import scrapy.crawler as 	   crawler


### selenium
# cf : https://stackoverflow.com/questions/30345623/scraping-dynamic-content-using-python-scrapy
# cf : https://stackoverflow.com/questions/17975471/selenium-with-scrapy-for-dynamic-page 
# cf : https://github.com/clemfromspace/scrapy-selenium 
from selenium 						import webdriver
from selenium.webdriver.support.ui 	import WebDriverWait
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep    

### cf : https://intoli.com/blog/running-selenium-with-headless-chrome/
### cf : https://duo.com/decipher/driving-headless-chrome-with-python
options_selenium = webdriver.ChromeOptions()
# options.binary_location = '/usr/local/bin/chromedriver'
options_selenium.add_argument('headless')
# option.add_argument(' — incognito')
# set the window size
options_selenium.add_argument('window-size=1200x600')
# initialize the driver
# driver = webdriver.Chrome(chrome_options=options_selenium)
### executable path for chrome driver
exec_chromedriver = "/usr/local/bin/chromedriver"


### settings scrapy

# s = get_project_settings()
# print "\ndefault settings scrapy : "
# pprint(dict(s))
# update settings from settings_scrapy.py
# s.update(dict(ITEM_PIPELINES={
# 	'openscraper.pipelines.RestExportPipeline': 300,
# }))
# print "\nupdated settings scrapy : "
# pprint(dict(s))


### SCRAPY PIPELINES....
# update setting to use the pipeline which will write results (items) in the database or files
# cf self-contained scrapy : https://gist.github.com/alecxe/fc1527d6d9492b59c610
# cf self-contained scrapy : https://github.com/kirankoduru/scrapy-programmatically/
# cf : https://stackoverflow.com/questions/42511814/scrapy-passing-custom-settings-to-spider-from-script-using-crawlerprocess-crawl

### set scrapy from settings_scrapy.py
settings = Settings()

settings.set( "BOT_NAME"					, BOT_NAME )
settings.set( "USER_AGENT"					, USER_AGENT )
# settings.set( "ROBOTSTXT_OBEY"				, ROBOTSTXT_OBEY )

settings.set( "ITEM_PIPELINES"				, ITEM_PIPELINES )

settings.set( "DB_DATA_URI" 				, DB_DATA_URI )
settings.set( "DB_DATA_DATABASE" 			, DB_DATA_DATABASE )
settings.set( "DB_DATA_COLL_SCRAP" 			, DB_DATA_COLL_SCRAP )


log_scrap.debug (">>> settings scrapy : \n %s \n", pformat(dict(settings)) )
# pprint(dict(settings))

log_scrap.debug ("--- run_generic_spider / BOT_NAME : %s", settings.get('BOT_NAME'))
log_scrap.debug ("--- run_generic_spider / USER_AGENT : %s",	settings.get('USER_AGENT'))
log_scrap.debug ("--- run_generic_spider / ITEM_PIPELINES : %s \n", settings.get('ITEM_PIPELINES').__dict__)




### import base_fields ###############
### import main args fom config.settings_corefields.py
from config.settings_corefields import * # mainly for DATAMODEL_CORE_FIELDS_ITEM

### import items
from items import * # GenericItem #, StackItem #ScrapedItem

### import mixins
# from mixins import GenericSpiderMixin




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


def clean_xpath_for_reactive(xpath_str, strings_to_clean) : 
	""" clean a string given a list of words/strings """
	for i in strings_to_clean : 
		xpath_str = xpath_str.replace(i, '')

	last_car = xpath_str[-1]
	if last_car == '/' : 
		xpath_str = xpath_str[:-1]
	return xpath_str


# to be used in GenericSpider class
'''
def dictFromDataModelList (datamodel_list ) : 
	"""creates a correspondance dict from datamodel to _xpath """
	
	# data_model_dict = { i : "{}_xpath".format(i) for i in datamodel_list }
	
	data_model_dict = { str(i["_id"]) : i for i in datamodel_list }
	
	return data_model_dict
'''



### ON ITEMS AND PIPELINES SEE : https://gist.github.com/alecxe/fc1527d6d9492b59c610

# class GenericSpiderUtils(Spider):

# 	"""a generic spider utils class to contain all parsing functions"""
	
# 	### spider class needs a default name
# 	name = "genericspiderutils"

# 	def __init__(self, user_id=None, datamodel=None, spider_id=None, spider_config_flat=None, *args, **kwargs) : 
		
# 		### super init/override spider class with current args 
# 		log_scrap.info("--- GenericSpider / __init__ :")

# 		super(GenericSpider, self).__init__(*args, **kwargs)


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### GENERIC SPIDER  #########################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

### note : to stop process cf : https://stackoverflow.com/questions/19071512/socket-error-errno-48-address-already-in-use 

class GenericSpider(Spider) :
	
	"""a generic spider to be configured with datamodel and spider_config_flat variables"""
	
	### spider class needs a default name
	name = "genericspider"

	def __init__(self, 	user_id				= None, 
						datamodel			= None, 
						spider_id			= None, 
						spider_config_flat	= None, 
						test_limit			= None,
						*args, **kwargs
				) : 
		

		print ("\n\n{}\n".format("> > > "*20))

		### super init/override spider class with current args 
		log_scrap.info("--- GenericSpider / __init__ :")

		super(GenericSpider, self).__init__(*args, **kwargs)
		
		self.user_id	= user_id
		self.spider_id 	= spider_id
		
		self.test_limit = test_limit
		log_scrap.info("--- GenericSpider / test_limit : %s ", self.test_limit )

		self.item_count = 0
		self.page_count = 1
		self.there_is_more_items_to_scrap = True 

		### store spider_config_flat
		log_scrap.info("--- GenericSpider / spider_config_flat : \n %s ", pformat(spider_config_flat) )
		self.spider_config_flat = spider_config_flat
		
		### global infos on spider
		self.spider_name 				= self.spider_config_flat['name']
		self.spider_url_root 			= self.spider_config_flat['page_url']
		self.spider_current_starturl 	= ""

		# self.settings_limit_pages = self.spider_config_flat['LIMIT']
		self.settings_limit_pages = self.spider_config_flat['LIMIT_PAGES']
		self.settings_limit_items = self.spider_config_flat['LIMIT_ITEMS']
		log_scrap.info("--- GenericSpider / settings_limit_pages : %s ", self.settings_limit_pages )
		log_scrap.info("--- GenericSpider / settings_limit_items : %s ", self.settings_limit_items )


		### get settings for selenium
		self.delay_driver 	= self.spider_config_flat['wait_driver'] 	# 5.0
		self.delay_new_page = self.spider_config_flat['wait_page'] 		# 1.5
		self.delay_implicit	= self.spider_config_flat['wait_implicit'] 	# 0.5
		# self.delay_item 	= self.spider_config_flat['LIMIT'] # 1.0

		### getting all the config args from spider_config_flat (i.e. next_page, ...)
		log_scrap.info("--- GenericSpider / passing kwargs..." ) 
		for k, v in spider_config_flat.iteritems() : 
			# log_scrap.info("  - %s : %s " %(k, v) )
			self.__dict__[k] = v


		### getting data model for later use in item
		log_scrap.info("--- GenericSpider / datamodel[:1] : \n %s \n ...", pformat(datamodel[:1]) ) 
		# self.datamodel = datamodel 
		# pprint (datamodel[:3])
		# print "..."

		### storing correspondance dict from datamodel
		self.dm_core 					= { i["field_name"] : { "field_type" : i["field_type"] } for i in datamodel if i["field_class"] == "core" }
		self.dm_core_item_related 		= DATAMODEL_CORE_FIELDS_ITEM
		
		self.dm_custom 					= { str(i["_id"]) 	: { "field_type" : i["field_type"], 
																"field_name" : i["field_name"] 
															} for i in datamodel if i["field_class"] == "custom" }
		log_scrap.info("--- GenericSpider / dm_custom : \n %s", pformat(self.dm_custom) ) 

		self.dm_custom_list 			= self.dm_custom.keys()

		self.dm_item_related 			= self.dm_custom_list + self.dm_core_item_related
		log_scrap.info("--- GenericSpider / dm_item_related : \n %s", pformat(self.dm_item_related) ) 



		### SPLASH
		### cf : https://blog.scrapinghub.com/2015/03/02/handling-javascript-in-scrapy-with-splash/


	def start_requests(self) :

		log_scrap.info("--- GenericSpider.start_requests ... " ) 

		for url in self.start_urls :
			
			log_scrap.info("--- GenericSpider.start_requests / url : %s ", url ) 
			self.spider_current_starturl = url

			log_scrap.info("--- GenericSpider.start_requests / starting first Scrapy request... " ) 
			yield Request(url=url, callback=self.parse, dont_filter=True)



	### parsing with scrapy
	def parse(self, response):
		""" parsing pages to scrap data with Scrapy requests"""

		### close spider if exception
		if 'Bandwidth exceeded' in response.body:
			raise CloseSpider('bandwidth_exceeded')
		
		log_scrap.debug("\n>>> NEW PARSING >>>\n" )
		log_scrap.info("--- GenericSpider.parse ..." )
		
		log_scrap.info("\n--- GenericSpider.parse /response  : \n%s" , response)
		log_scrap.info("\n--- GenericSpider.parse /response  : \n%s \n" , response.__dict__.keys() )

		# for k, v in response.__dict__.iteritems() : 
		# 	log_scrap.info("\n--- [k] {} : [v] {} : ".format(k,v))
		# print response._body




		### TO DO ### 
		### start request with API crawler
		if self.spider_config_flat["parse_api"] == True :

			log_scrap.info("\n--- GenericSpider.parse / starting request on API endpoint... " ) 
			jsonresponse = json.loads(response.body_as_unicode())
			log_scrap.info("--- GenericSpider.parse / jsonresponse : \n%s", jsonresponse )

			raw_items_list = jsonresponse[self.item_xpath]
			log_scrap.info("--- GenericSpider.parse / raw_items_list : \n%s\n...", raw_items_list[0] )

			### start parsing page : loop through data items in page in response
			for raw_data in raw_items_list :
				
				if self.there_is_more_items_to_scrap : 

					self.item_count += 1

					### check if can continue depending on item_count
					if self.settings_limit_items == 0 or self.item_count <= self.settings_limit_items : 
						
						print()
						log_scrap.debug(">>> NEW ITEM - spider_url_root : {} >>>".format(self.spider_url_root) )
						log_scrap.debug(">>> NEW ITEM - spider_current_starturl : {} >>>".format(self.spider_current_starturl) )
						log_scrap.debug(">>> NEW ITEM - Scrapy - item n°{} >>> \n".format(self.item_count) )

						### instantiate Item to fill from datamodel --> cf items.py 
						itemclass 	= create_item_class( 'GenericItemClass', fields_list = self.dm_item_related )
						item 		= itemclass()

						### add global info to item : i.e. core fields in dm_core_item_related list
						item[ 'spider_id' ]		= self.spider_id
						item[ 'added_by'  ]		= self.user_id 
						item[ 'added_at'  ]		= time.time()		# timestamp
						item[ 'link_src'  ]		= response._url

						### TO DO : switcher inside ###
						### extract data and feed it to the Item instance based on spider_config_flat
						item = self.fill_item_from_results_page(raw_data, item)

						yield item

					else : 
						log_scrap.warning("--- GenericSpider. / OUT OF LIMIT_ITEMS - items count : {} - LIMIT_ITEMS : {}".format(self.item_count, self.LIMIT_ITEMS) )
						raise CloseSpider('OUT OF LIMIT_ITEMS')

				else : 
					log_scrap.warning("--- GenericSpider. / OUT OF ITEMS - items count : {} - LIMIT_ITEMS : {}".format(self.item_count, self.LIMIT_ITEMS) )
					raise CloseSpider('OUT OF ITEMS')


		### start requests with pure Scrapy requests
		elif self.spider_config_flat["parse_reactive"] == False :

			log_scrap.info("\n--- GenericSpider.parse / starting requests with Scrapy... " ) 
			# self.parse_scrapy(response)

			### find items list
			log_scrap.info("--- GenericSpider.parse / self.item_xpath : %s", self.item_xpath )
			raw_items_list = response.xpath(self.item_xpath)
			log_scrap.info("--- GenericSpider.parse / len(raw_items_list) : %d ", len(raw_items_list) )


			### start parsing page : loop through data items in page in response
			if len(raw_items_list) != 0 :
				for raw_data in raw_items_list :
					
					self.item_count += 1

					### check if can continue depending on item_count
					if self.settings_limit_items == 0 or self.item_count <= self.settings_limit_items : 
						
						print()
						log_scrap.debug(">>> NEW ITEM - spider_url_root : {} >>>".format(self.spider_url_root) )
						log_scrap.debug(">>> NEW ITEM - spider_current_starturl : {} >>>".format(self.spider_current_starturl) )
						log_scrap.debug(">>> NEW ITEM - Scrapy - item n°{} / page n°{} >>> \n".format(self.item_count, self.page_count) )

						# print ">>> raw_data : \n", raw_data.extract()

						### instantiate Item to fill from datamodel --> cf items.py 
						itemclass 	= create_item_class( 'GenericItemClass', fields_list = self.dm_item_related )
						item 		= itemclass()

						### add global info to item : i.e. core fields in dm_core_item_related list
						item[ 'spider_id' ]		= self.spider_id
						item[ 'added_by'  ]		= self.user_id 
						item[ 'added_at'  ]		= time.time()		# timestamp
						item[ 'link_src'  ]		= response._url

						### extract data and feed it to the Item instance based on spider_config_flat
						item = self.fill_item_from_results_page(raw_data, item)
						

						### if need to follow to extract all data
						if self.spider_config_flat["parse_follow"] == True : 

							log_scrap.debug(">>> FOLLOW LINK - item n°{} / page n°{} >>>>>> \n".format(self.item_count, self.page_count) )
							log_scrap.info("--- GenericSpider. / self.follow_xpath : %s", self.follow_xpath )

							follow_link 	= raw_data.xpath( self.follow_xpath ).extract_first()	
							# log_scrap.info(" --> follow_link RAW : %s ", follow_link )
							# complete follow link if needed
							follow_link = self.clean_link(follow_link)		
							log_scrap.info(" --> follow_link CLEAN : %s ", follow_link )

							# store follow_link
							item[ 'link_data' ]	= follow_link
							url 				= item['link_data']

							try : 
								yield scrapy.Request(url, callback=self.parse_detailed_page, meta={'item': item})

							except :
								yield item

						### if no follow link
						else : 		

							### item completion is finished - yield and so spark pipeline for item (store in db for instance)
							# log_scrap.info(">>> GenericSpider.parse - item.items() : \n %s", item.items() )
							# log_scrap.info(">>> GenericSpider.parse - item.keys()  : \n %s", item.items() )
							yield item

							# print ("\n>>> NEXT ITEM " + ">>> >>> "*10, "\n")

						log_scrap.info(" --> item : \n %s \n", pformat(item) )

					else : 
						log_scrap.warning("--- GenericSpider. / OUT OF LIMIT_ITEMS - items count : {} - LIMIT_ITEMS : {}".format(self.item_count, self.LIMIT_ITEMS) )
						raise CloseSpider('OUT OF LIMIT_ITEMS')

			else : 
				self.there_is_more_items_to_scrap = False
				log_scrap.warning("--- GenericSpider. / OUT OF TEST_LIMIT - items count : {} - LIMIT_ITEMS : {} / except -> break".format(self.item_count, self.LIMIT_ITEMS) )
				raise CloseSpider('OUT OF ITEMS')

			### check if there is a test_limit
			if self.test_limit == None or self.page_count < self.test_limit : 

				if self.page_count < self.settings_limit_pages or self.settings_limit_pages == 0 :

					log_scrap.info("--- GenericSpider.parse (Scrapy)  >>> PAGE n°{} DONE -> NEXT PAGE >>> \n".format(self.page_count) )

					### get and go to next page 
					is_next_page, next_page = self.get_next_page(response)

					if is_next_page :
											
						self.page_count += 1

						log_scrap.debug(">>> NEXT PAGE - spider_url_root : {} >>>".format(self.spider_url_root) )
						log_scrap.debug(">>> NEXT PAGE - spider_current_starturl : {} >>>".format(self.spider_current_starturl) )
						log_scrap.info("--- GenericSpider.parse >>> NEXT PAGE I  : %s", next_page )
						next_page = self.clean_link(next_page)	
						log_scrap.info("--- GenericSpider.parse >>> NEXT PAGE II : %s", next_page )

						yield response.follow(next_page, callback=self.parse)

					else :
						self.there_is_more_items_to_scrap = False
						log_scrap.warning("--- GenericSpider. / NO MORE PAGE TO SCRAP - pages count : {} ".format(self.page_count) )
						raise CloseSpider('NO MORE PAGE TO SCRAP')

				else :
					self.there_is_more_items_to_scrap = False
					log_scrap.warning("--- GenericSpider. / OUT OF TEST_LIMIT - page n°{} - limit : {} - test_limit : {} / except -> break".format(self.page_count, self.settings_limit_pages, self.test_limit) )
					raise CloseSpider('OUT OF TEST_LIMIT')

			else : 
				self.there_is_more_items_to_scrap = False
				log_scrap.warning("--- GenericSpider. / OUT OF TEST_LIMIT - items count : {} - LIMIT_ITEMS : {} / except -> break".format(self.item_count, self.LIMIT_ITEMS) )
				raise CloseSpider('OUT OF TEST_LIMIT')


		### start requests with Selenium
		else :
			### initiate selenium browser
			### cf : https://github.com/voliveirajr/seleniumcrawler/blob/master/seleniumcrawler/spiders/seleniumcrawler_spider.py 
			log_scrap.info("\n--- GenericSpider.parse / starting Selenium driver... " ) 
			
			### specify executable path to launch webdriver--> 
			# cf : where chromedriver was installed when `brew install chromedriver`
			self.driver = webdriver.Chrome(executable_path=exec_chromedriver, chrome_options=options_selenium)
			# self.driver = webdriver.Chrome(chrome_options=options_selenium)
			# self.driver = webdriver.Firefox()
			# self.driver = webdriver.Chrome()
			# self.driver = webdriver.PhantomJS() ### deprecated

			### setup waiting times
			self.wait_driver	= WebDriverWait(self.driver, self.delay_driver)
			self.wait_page 		= WebDriverWait(self.driver, self.delay_new_page)
			self.driver.implicitly_wait(self.delay_implicit)
			log_scrap.debug("--- GenericSpider. / self.delay_driver   : %s", self.delay_driver )
			log_scrap.debug("--- GenericSpider. / self.delay_new_page : %s", self.delay_new_page )
			log_scrap.debug("--- GenericSpider. / self.delay_implicit : %s", self.delay_implicit )

			
			### start parsing with selenium
			log_scrap.debug("--- GenericSpider. / response._url       : %s", response._url )
			self.driver.get(response._url)
			log_scrap.info("--- GenericSpider. / url '{}' is loaded ... ".format( response._url ))


			### clean original xpath from strings
			strings_to_clean = [
				'/@src',
				'/@href',
				'/text()',
				'/@*[name()="xlink:href"]',
				'/@datetime'
			]
			
			while self.there_is_more_items_to_scrap : 
			
				log_scrap.debug("--- GenericSpider. / while loop continues : %s", self.there_is_more_items_to_scrap )

				try : 

					### debug page content
					page_source_code = self.driver.page_source.encode("utf-8")
					log_scrap.debug("--- GenericSpider. / page_source_code : \n %s ", page_source_code )

					### start parsing page : 
					log_scrap.info("--- GenericSpider. / self.item_xpath : %s", self.item_xpath )
					raw_items_list 	= self.driver.find_elements_by_xpath(self.item_xpath)
					log_scrap.info("--- GenericSpider. / raw_items_list length : %s", len(raw_items_list) )
					# log_scrap.info("--- GenericSpider. / raw_items_list[0].text : \n%s", raw_items_list[0].text )
					
					# current_item_index = 0

					# loop through data items in page in response
					if len(raw_items_list) != 0 : 
						for raw_data in raw_items_list :

							### add +1 to items count 
							self.item_count += 1

							log_scrap.debug("--- GenericSpider. / VARIABLES - item n°{} - there_is_more_items_to_scrap : {} ".format(self.item_count, self.there_is_more_items_to_scrap) )

							### check if can continue depending on item_count
							if self.settings_limit_items == 0 or self.item_count <= self.settings_limit_items : 
								
								log_scrap.debug(">>> NEW ITEM - spider_url_root : {} >>>".format(self.spider_url_root) )
								log_scrap.debug(">>> NEW ITEM - spider_current_starturl : {} >>>".format(self.spider_current_starturl) )
								log_scrap.debug(">>> NEW ITEM - Selenium - item n°{} / page n°{} >>> \n".format(self.item_count, self.page_count) )

								### instantiate Item to fill from datamodel --> cf items.py 
								itemclass 	= create_item_class( 'GenericItemClass', fields_list = self.dm_item_related )
								item 		= itemclass()

								### add global info to item : i.e. core fields in dm_core_item_related list
								item[ 'spider_id' ]		= self.spider_id
								item[ 'added_by'  ]		= self.user_id 
								item[ 'added_at'  ]		= time.time()		# timestamp
								item[ 'link_src'  ]		= response._url

								### extract data and feed it to the Item instance based on spider_config_flat
								item = self.fill_item_from_results_page(raw_data, item, is_reactive=True, strings_to_clean=strings_to_clean )

								### find follow link to open detailled item view
								if self.spider_config_flat["parse_follow"] == True :
									
									log_scrap.debug(">>> FOLLOW LINK - item n°{} / page n°{} >>>>>> \n".format(self.item_count, self.page_count) )
									log_scrap.info("--- GenericSpider. / self.follow_xpath : %s", self.follow_xpath )

									### follow link with Scrapy
									try : 
										log_scrap.debug("--- GenericSpider. / follow link with Scrapy ..." )

										# log_scrap.debug("--- GenericSpider. /  get href of follow_link ..." )
										follow_link_xpath 	= clean_xpath_for_reactive(self.follow_xpath, strings_to_clean)
										follow_link			= raw_data.find_element_by_xpath( follow_link_xpath ).get_attribute('href')

										# log_scrap.info(" --> follow_link RAW : %s ", follow_link )
										# complete follow link if needed
										follow_link = self.clean_link(follow_link)	
										log_scrap.info(" --> follow_link CLEAN : %s ", follow_link )

										# store follow_link
										item[ 'link_data' ]	= follow_link
										url_follow			= item['link_data']

										try : 
											yield scrapy.Request(url_follow, callback=self.parse_detailed_page, meta={'item': item})

										except :
											yield item


									### follow link with Selenium
									### NOT TESTED YET
									### FIND A WEBSITE TEST FOR REACTIVE DETAILLED PAGES
									except : 
										log_scrap.debug("--- GenericSpider. / follow link with Selenium ..." )

										follow_link_xpath 	= clean_xpath_for_reactive(self.follow_xpath, strings_to_clean)
										log_scrap.info("--- GenericSpider. / self.follow_link_xpath : %s", self.follow_link_xpath )
										follow_link 		=  raw_data.find_element_by_xpath( follow_link_xpath )
										
										### open link in new tab ?
										follow_link.click()

										### get data and save data
										try :
											log_scrap.debug("--- GenericSpider. / get data and save data ..." )
											item = self.fill_item_from_results_page(raw_data, item, is_reactive=True, strings_to_clean=strings_to_clean )
											
											### back to previous page and scrap from where it left
											### cf : https://selenium-python.readthedocs.io/navigating.html#navigation-history-and-location
											self.driver.back()
											
											yield item 

										except : 
											yield item

								### if no follow link
								else : 
									yield item

								log_scrap.info(" --> item : \n %s \n", pformat(item) )

							else :
								self.there_is_more_items_to_scrap = False
								log_scrap.warning("--- GenericSpider. / OUT OF LIMIT_ITEMS - items count : {} - LIMIT_ITEMS : {} / except -> break".format(self.item_count, self.LIMIT_ITEMS) )
								self.driver.close()
								log_scrap.info("--- GenericSpider / driver is shut" ) 
								# raise CloseSpider('OUT OF LIMIT_ITEMS')
								break

					else : 
						self.there_is_more_items_to_scrap = False 
						log_scrap.warning("--- GenericSpider. / OUT OF ITEMS - page n°{} - limit : {} - test_limit : {} / except -> break".format(self.page_count, self.settings_limit_pages, self.test_limit) )
						self.driver.close()
						log_scrap.info("--- GenericSpider / driver is shut" ) 
						# raise CloseSpider('OUT OF TEST_LIMIT')
						break

					if self.test_limit == None or self.page_count < self.test_limit :
						
						if self.there_is_more_items_to_scrap : 

							if self.page_count < self.settings_limit_pages or self.settings_limit_pages == 0 :

								print ()
								log_scrap.info("\n --- GenericSpider.parse (Selenium)  >>> PAGE n°{} DONE -> NEXT PAGE >>> \n".format(self.page_count) )

								### add +1 to parsed pages
								self.page_count += 1

								log_scrap.debug(">>> NEXT PAGE - spider_url_root : {} >>>".format(self.spider_url_root) )
								log_scrap.debug(">>> NEXT PAGE - spider_current_starturl : {} >>>".format(self.spider_current_starturl) )

								### find next page btn in current view
								log_scrap.info("--- GenericSpider. / self.next_page : %s", self.next_page )
								next_page_xpath = clean_xpath_for_reactive(self.next_page, strings_to_clean)
								log_scrap.info("--- GenericSpider. / next_page_xpath : %s", next_page_xpath )
								# next_page 	= re.sub("|".join(strings_to_clean), "", next_page )
								
								# try :
								# element_present = EC.presence_of_element_located((By.XPATH, next_page_xpath ))
								# log_scrap.info("--- GenericSpider. / next_page present : %s", element_present )
								# self.wait.until(element_present)
								# next_page = self.wait.until( EC.element_to_be_clickable(element_present) )
								# next_page 		= self.driver.find_element_by_xpath( next_page_xpath )
								next_page 		= self.driver.find_element(By.XPATH, next_page_xpath )
								
								log_scrap.info("--- GenericSpider. / next_page : %s", next_page )
								log_scrap.info("--- GenericSpider. / next_page.text : %s", next_page.text )
								
								# except TimeoutException:
								# except :
								# 	log_scrap.error("--- GenericSpider. / Timed out waiting for page to load")
								
								
								
								### click next button and wait for ajax calls to complete (post and get)
								### cf : http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
								
								# def wait_for(condition_function):
								# 		start_time = time.time() 
								# 	while time.time() < start_time + 3: 
								# 		if condition_function(): 
								# 			return True 
								# 		else: 
								# 			time.sleep(0.1) 
								# 	raise Exception ('Timeout waiting for {}'.format(condition_function.__name__) )

								# def link_has_gone_stale():
								# 		try:
								# 		# poll the link with an arbitrary call
								# 		next_page.find_elements_by_xpath(self.item_xpath) 
								# 		return False
								# 	except StaleElementReferenceException :
								# 		return True

								log_scrap.debug("--- ... ---")
								try : 
									log_scrap.info("--- GenericSpider. / next_page.click() " )
									next_page.click()
								except : 
									# log_scrap.info("--- GenericSpider. / next_page.send_keys( \ n )" )
									# next_page.send_keys("\n")
									# added this step for compatibility of scrolling to the view
									log_scrap.error("--- GenericSpider. / ALTERNATIVE next_page.click() " )
									# self.driver.execute_script("return arguments[0].scrollIntoView();", next_page)
									# next_page.click()
									self.driver.execute_script("arguments[0].click();", next_page)
								
								### wait after click
								try :
									log_scrap.info("--- GenericSpider. / wait for ajax to finish... " )
									# wait_for(link_has_gone_stale)
									self.wait_page.until(lambda driver: self.driver.execute_script('return jQuery.active') == 0)
									self.wait_page.until(lambda driver: self.driver.execute_script('return document.readyState') == 'complete')
									# time.sleep(self.delay_implicit)
									time.sleep(self.delay_new_page) 
								except : 
									log_scrap.error("--- GenericSpider. / !!! FAIL / wait for ajax to finish... " )


							
							else :
								there_is_more_items_to_scrap = False
								log_scrap.warning("--- GenericSpider. / OUT OF PAGES TO SCRAP - page n°{} / except -> break".format(self.page_count) )
								self.driver.close()
								# raise CloseSpider('OUT OF PAGES TO SCRAP')
								break

					else :
						self.there_is_more_items_to_scrap = False
						log_scrap.warning("--- GenericSpider. / OUT OF TEST_LIMIT - page n°{} - limit : {} - test_limit : {} / except -> break".format(self.page_count, self.settings_limit_pages, self.test_limit) )
						self.driver.close()
						log_scrap.info("--- GenericSpider / driver is shut" ) 
						# raise CloseSpider('OUT OF TEST_LIMIT')
						break

				except :
					log_scrap.warning("--- GenericSpider. / NO MORE ITEMS TO SCRAP - item_count : {} - LIMIT_ITEMS : {} / except -> break".format(self.item_count, self.LIMIT_ITEMS) )
					self.driver.close()
					log_scrap.info("--- GenericSpider / driver is shut" ) 
					# raise CloseSpider('NO MORE ITEMS TO SCRAP')
					break



	
		

	### generic function to fill item from result
	def fill_item_from_results_page (self, 
										raw_data, item, 
										is_reactive=False, 
										strings_to_clean=None,
										) : 
		""" fill item """

		log_scrap.debug(" -+- fill_item_from_results_page : item n°{}".format( self.item_count ) )
		# log_scrap.info(" -+- item : \n %s \n", pformat(item) )
		# log_scrap.info(" -+- raw_data : \n %s \n", pformat(raw_data) )

		### extract data and feed it to Item instance based on spider_config_flat
		for dm_field in self.dm_custom_list : 
			
			### first, checks if xpath exists in spider_config_flat
			if dm_field in self.spider_config_flat : 

				### check if field filled in spider_config_flat is not empty
				if self.spider_config_flat[ dm_field ] != [] and self.spider_config_flat[ dm_field ] != "" :
		
					full_data = None
					# dm_name   = str( self.dm_custom[dm_field]["field_name"] )
					dm_name   = self.dm_custom[dm_field]["field_name"]
					# log_scrap.info(" -+- extract / dm_name : %s ", dm_name )

					### fill item field corresponding to xpath
					item_field_xpath 	= self.spider_config_flat[ dm_field ]					

					### extract data with Scrapy request
					if is_reactive == False : 
						try :
							# log_scrap.debug(" -+- extract / with Scrapy ... " )
							# log_scrap.info(" -+- extract / item_field_xpath : {} ".format(item_field_xpath ))
							log_scrap.info(" -+- extract / dm_name : %s - item_field_xpath : %s " %(dm_name, item_field_xpath ))
							full_data 			= raw_data.xpath( item_field_xpath ).extract()
						except :
							log_scrap.error(" -+- !!! extract FAILED / with Scrapy ... " )

					### extract data with Selenium
					else :
						try :
							# log_scrap.debug(" -+- extract / with Selenium ... " )
							# item_field_xpath 	= re.sub("|".join(strings_to_clean), "", item_field_xpath )
							item_field_xpath = clean_xpath_for_reactive(item_field_xpath, strings_to_clean)
							# log_scrap.info(" -+- extract / item_field_xpath : {} ".format(item_field_xpath ))
							log_scrap.info(" -+- extract / dm_name : %s - item_field_xpath : %s " %(dm_name, item_field_xpath ))

							# element_present = EC.presence_of_element_located((By.XPATH, item_field_xpath ))
							# log_scrap.info(" -+- extract / item_field_xpath present : %s ", element_present )
							# try : 
								# WebDriverWait(self.driver, self.delay_item).until(element_present)
							
							full_data_list 	= raw_data.find_elements_by_xpath( item_field_xpath )
							full_data 		= [ data.text for data in full_data_list ]
							# log_scrap.info(" -+- extract / full_data : %s ", full_data )
							# except TimeoutException:
							# 	log_scrap.error("-+- extract FAILED / Timed out waiting for page to load")
						except :
							log_scrap.error(" -+- !!! extract FAILED / with Selenium ... " )

					# log_scrap.warning(
					# 	" \n field_name : {} \n item_field_xpath : {} \n dm_field : {} \n full_data : ... ".format(
					# 		self.dm_custom[dm_field]["field_name"],
					# 		item_field_xpath,
					# 		dm_field,
					# 		# full_data 
					# 	)
					# )

					# check if data exists at all
					if full_data != None and full_data != [] and full_data != [u""] : 
						
						# log_scrap.debug(" -+- extract / full_data ..." )

						### clean data from break lines etc...
						full_data = self.clean_data_list(full_data)
						# log_scrap.info(" -+- extract / full_data : %s ", full_data )

						### in case data needs cleaning before storing
						if self.dm_custom[dm_field]["field_type"] in ["url", "image"]  : 
							clean_href_list = []
							for data in full_data : 
								if data != None or data != u"" : 
									data = self.clean_link(data)
									clean_href_list.append(data)
							full_data = clean_href_list

						# delete duplicates and aggregate
						if full_data != None or full_data != [] or full_data != [u""] : 
							
							# delete duplicates
							full_data_uniques 	= set(full_data)
							full_data_clean 	= list(full_data_uniques)

							# aggregate to existing results
							if dm_field in item : 
								item[ dm_field ] = item[ dm_field ] + full_data_clean
							else : 
								item[ dm_field ] = full_data_clean


		
		log_scrap.warning(">>> ITEM n°{} / page n°{} >>> END OF : fill_item_from_results_page >>>".format(self.item_count, self.page_count))
		# log_scrap.warning("\n %s \n", pformat(item))

		return item


	### go to follow link and retrieve remaining data for Item
	def parse_detailed_page (self, response) :
		""" parse_detailed_page """
		
		item = response.meta["item"]

		if self.there_is_more_items_to_scrap :

			log_scrap.info(" === GenericSpider / parse_detailed_page ... " )
			log_scrap.debug("=== GenericSpider / VARIABLES - item n°{} - there_is_more_items_to_scrap : {} ".format(self.item_count, self.there_is_more_items_to_scrap) )

			item = self.fill_item_from_results_page(response, item)

		yield item

	
	### follow up and callbacks
	def get_next_page(self, response):
		"""
		tries to find a new page to scrap.
		if it finds one, returns it along with a True value
		"""
		
		log_scrap.info(" === GenericSpider / get_next_page ... " )
		log_scrap.debug("=== GenericSpider / VARIABLES - item n°{} - there_is_more_items_to_scrap : {} ".format(self.item_count, self.there_is_more_items_to_scrap) )

		try :
			next_page = response.xpath(self.next_page).extract_first()
		except :
			next_page = None 

		log_scrap.info(" === GenericSpider.get_next_page / next_page I : %s ", next_page )

		if (next_page is not None) and (self.page_count < self.settings_limit_pages ) :
			
			log_scrap.info(" === GenericSpider.get_next_page / self.spider_config_flat['next_page'] : %s ", self.spider_config_flat[ "next_page" ] )
			# self.page_count += 1
			# next_page = next_page.strip()
			# next_page = self.add_string_to_complete_url_if_needed(next_page, self.page_url)
			try : 
				next_page = response.xpath(self.spider_config_flat[ "next_page" ]).extract_first()
				log_scrap.info(" === GenericSpider.get_next_page / next_page II : %s ", next_page )
				return True, next_page
			
			except:
				return False, next_page
		
		else:
			return False, next_page


	### clean a link if http is missing
	def clean_link(self, link=None):
		""" complete a link if needed """
		
		### erase all spaces in original link
		link = ' '.join(link.split())
		link = link.replace(" ","").replace('\n', '').replace('\r', '')
		
		if "@" in link :
			if link.startswith("mailto"):
				pass
				# return link
			else :
				link = "mailto:" + link
				# return link

		elif not link.startswith("http"): 
			separator = ""
			if not link.startswith("/"):
				separator = "/"
			link 	= "{}{}{}".format( self.page_url, separator, link)			
			# return link
		
		# else : 
		# 	return link

		return link


	### clean data from trailing spaces, multiple spaces, line breaks, etc...
	def clean_data_list(self, data_list, chars_to_strip = STRIP_STRING ):
		""" clean data list from trailing """

		clean_data_list = []
		
		for data in data_list : 
			
			# replace multiple spaces
			data = ' '.join(data.split())

			# remove line breaks
			if data in DATA_CONTENT_TO_IGNORE : 
				pass
			else : 
				data = data.strip(chars_to_strip)
				clean_data_list.append(data)
		
		return clean_data_list




### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### SPIDER RUNNER ###########################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###


### define the spider runner
### cf : https://stackoverflow.com/questions/13437402/how-to-run-scrapy-from-within-a-python-script
### cf : https://doc.scrapy.org/en/latest/topics/practices.html
### solution chosen from : https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable 

def run_generic_spider( user_id				= None, 
						spider_id			= None, 
						datamodel			= None, 
						run_spider_config	= None,
						test_limit			= None 
						):
	"""
	just launch run_generic_spider() from any handler in controller
	"""

	print ()
	log_scrap.info("--- run_generic_spider / spider_id : %s ", spider_id )
	
	# !!! spider is launched from main.py level !!! 
	# all relative routes referring to this...
	log_scrap.info("--- run_generic_spider / os.getcwd() : %s ", os.getcwd()  )

	### flattening run_spider_config : from nested to flat dict 
	log_scrap.info("--- run_generic_spider / 'flattenSpiderConfig()' on 'run_spider_config' --> 'spider_config_flat' ..." )
	spider_config_flat = flattenSpiderConfig( run_spider_config )


	### settings for crawler
	# cf : https://hackernoon.com/how-to-crawl-the-web-politely-with-scrapy-15fbe489573d
	
	### global settings for scrapy processes (see upper)
	log_scrap.info("--- run_generic_spider / BOT_NAME :       %s ", settings.get('BOT_NAME') ) 
	log_scrap.info("--- run_generic_spider / USER_AGENT :     %s ", settings.get('USER_AGENT') )
	log_scrap.info("--- run_generic_spider / ITEM_PIPELINES : %s ", settings.get('ITEM_PIPELINES').__dict__ )
	# specific settings for this scrapy process
	settings.set( "CURRENT_SPIDER_ID" 				, spider_id )
	settings.set( "RANDOMIZE_DOWNLOAD_DELAY"		, RANDOMIZE_DOWNLOAD_DELAY )
	
	### custom settings for scrapy process
	# settings.set( "DOWNLOAD_DELAY" 				, DOWNLOAD_DELAY )
	settings.set( "DOWNLOAD_DELAY" 					, spider_config_flat["download_delay"] )


	### initiating crawler process
	log_scrap.info("--- run_generic_spider / instanciate process ..." 	 )
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
										spider_config_flat	= spider_config_flat,
										test_limit			= test_limit 
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

	
	
	print ("\n\n{}\n".format("> > > "*20))





#############################################
### cool snippets 

	### convert to class object
	# spider = globals()[spider]