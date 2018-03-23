# -*- encoding: utf-8 -*-

# import 	pprint
from 	pprint import pprint, pformat
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
pprint(dict(settings))

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

# class GenericSpiderUtils(Spider):

# 	"""a generic spider utils class to contain all parsing functions"""
	
# 	### spider class needs a default name
# 	name = "genericspiderutils"

# 	def __init__(self, user_id=None, datamodel=None, spider_id=None, spider_config_flat=None, *args, **kwargs) : 
		
# 		### super init/override spider class with current args 
# 		log_scrap.info("--- GenericSpider / __init__ :")

# 		super(GenericSpider, self).__init__(*args, **kwargs)




class GenericSpider(Spider) :
	
	"""a generic spider to be configured with datamodel and spider_config_flat variables"""
	
	### spider class needs a default name
	name = "genericspider"

	def __init__(self, user_id=None, datamodel=None, spider_id=None, spider_config_flat=None, *args, **kwargs) : 
		

		print "\n\n{}\n".format("> > > "*20)

		### super init/override spider class with current args 
		log_scrap.info("--- GenericSpider / __init__ :")

		super(GenericSpider, self).__init__(*args, **kwargs)
		
		self.user_id	= user_id
		self.spider_id 	= spider_id
		
		self.item_count = 0
		self.page_count = 1


		### store spider_config_flat
		log_scrap.info("--- GenericSpider / spider_config_flat : \n %s ", pformat(spider_config_flat) )
		self.spider_config_flat = spider_config_flat

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



	def parse(self, response):
		""" parsing pages to scrap data """


		print "\n>>> NEW PARSING " + ">>> >>> "*10, "\n"
		log_scrap.info("--- GenericSpider.parse ..." )
		
		# print response
		# print response.__dict__.keys()
		# for k, v in response.__dict__.iteritems() : 
		# 	print k ,"---", v
		# print response._body

		# log_scrap.info(" response.xpath : \n %s ", pformat (response.xpath(self.item_xpath)[0] ))


		### TO DO !
		### check response to see if API or HTML response
		log_scrap.info("--- GenericSpider.parse / self.item_xpath : %s", self.item_xpath )
		




		raw_items_list = response.xpath(self.item_xpath)
		# raw_items_list = response.xpath('//table[@class="sobi2Listing"]/tr')
		log_scrap.info("--- GenericSpider.parse / len(raw_items_list) : %d ", len(raw_items_list) )

		### start parsing page : 
		# loop through data items in page in response
		for raw_data in raw_items_list :
			
			print "\n>>> NEW ITEM " + ">>> >>> "*10, "\n"
			self.item_count += 1

			print ">>> raw_data : \n", raw_data.extract()

			### instantiate Item to fill from datamodel --> cf items.py 
			itemclass 	= create_item_class( 'GenericItemClass', fields_list = self.dm_item_related )
			item 		= itemclass()

			### add global info to item : i.e. core fields in dm_core_item_related list
			item[ 'spider_id' ]		= self.spider_id
			item[ 'added_by'  ]		= self.user_id 
			item[ 'added_at'  ]		= time.time()		# timestamp
			item[ 'link_src' ]		= response._url


			### extract data and feed it to the Item instance based on spider_config_flat
			item = self.fill_item_from_results_page(raw_data, item)
			
			print "\n>>> NEXT ITEM " + ">>> >>> "*10, "\n"



			### if need to follow to extract all data
			if self.spider_config_flat["parse_follow"] == True : 
				
				# extract follow link
				follow_link 	= raw_data.xpath( self.follow_xpath ).extract_first()	
				log_scrap.info(" --> follow_link RAW : %s ", follow_link )


				# complete follow link if needed
				follow_link = self.clean_link(follow_link)
				# if not follow_link.startswith("http"): 
				# 	separator = ""
				# 	if not follow_link.startswith("/"):
				# 		separator = "/"
				# 	follow_link 	= "{}{}{}".format( self.page_url, separator, follow_link)			


				log_scrap.info(" --> follow_link CLEAN : %s ", follow_link )

				item[ 'link_data' ]	= follow_link
				
				url 				= item['link_data']
				log_scrap.info(" --> item : %s ", item )

				try : 
					# yield scrapy.Request(url, callback=self.parse_detailed_page, meta={'item': item})
					yield scrapy.Request(url, callback=self.parse_detailed_page, meta={'item': item})
				
				except :
					yield item

			else : 			
				### item completion is finished - yield and so spark pipeline for item (store in db for instance)
				# print "\nGenericSpider.parse - item : \n", item.items()
				# print item.keys()
				yield item

				print "\n>>> NEXT ITEM " + ">>> >>> "*10, "\n"



		### get and go to next page 
		# next_page_url = response.xpath(self.spider_config_flat[ "next_page_xpath" ]).extract_first()
		# if next_page_url is not None:
		# 	print "\n --- GenericSpider.parse / NEXT PAGE... \n"
		# 	# yield scrapy.Request(response.urljoin(next_page_url))
		# 	yield scrapy.follow(response.urljoin(next_page_url, callback=self.parse))
		is_next_page, next_page = self.get_next_page(response)
		if is_next_page:
			
			print

			self.page_count += 1

			log_scrap.info(" --- GenericSpider.parse >>> NEXT PAGE... \n" )
			
			yield response.follow(next_page, callback=self.parse)



	### generic function to fill item from result
	def fill_item_from_results_page (self, raw_data, item ) : 
		""" fill item """

		log_scrap.info("-+- fill_item_from_results_page" )
		print item

		### extract data and feed it to Item instance based on spider_config_flat
		for dm_field in self.dm_custom_list : 
			
			### first, checks if xpath exists in spider_config_flat
			if dm_field in self.spider_config_flat : 
				
				# log_scrap.info("\n dm_field : %s | dm_name : %s ", 
				# 						dm_field, 
				# 						self.dm_custom[dm_field]["field_name"] )

				### check if field filled in spider_config_flat is not empty
				if self.spider_config_flat[ dm_field ] != [] and self.spider_config_flat[ dm_field ] != "" :
		
					### fill item field corresponding to xpath
					item_field_xpath 	= self.spider_config_flat[ dm_field ]					
					
					full_data 			= raw_data.xpath( item_field_xpath ).extract()
					log_scrap.warning("\n field_name : %s \n dm_field : %s \n full_data : %s ", 
										self.dm_custom[dm_field]["field_name"],
										dm_field,
										full_data )

					### in case data needs cleaning before storing
					if self.dm_custom[dm_field]["field_type"] in ["url", "image"] : 
						full_data = self.clean_link(full_data)
					
					if full_data != None or full_data != [] : 
						
						# delete duplicates
						full_data_uniques 	= set(full_data)
						full_data_clean 	= list(full_data_uniques)

						# aggregate to results
						if dm_field in item : 
							item[ dm_field ] = item[ dm_field ] + full_data_clean
						else : 
							item[ dm_field ] = full_data_clean

					# 	if item[ dm_field ] == [] or item[ dm_field ] == None : 
					# 		item[ dm_field ] 	= full_data
					# 	else :
					# 		item[ dm_field ] 	= item[ dm_field].append(full_data)
		
		print "\n>>> ITEM >>> after fill_item_from_results_page >>>"
		print item
		print 

		return item


	### go to follow link and retrieve remaining data for Item
	def parse_detailed_page (self, response) :
		""" """

		log_scrap.info(" === GenericSpider.parse / parse_detailed_page / ... " )
		print response._body

		item = response.meta["item"]
		item = self.fill_item_from_results_page(response, item)

		print 
		yield item


	### follow up and callbacks
	def get_next_page(self, response):
		"""
		tries to find a new page to scrap.
		if it finds one, returns it along with a True value
		"""
		
		next_page = response.xpath(self.next_page).extract_first()
		
		if (next_page is not None) and (self.page_count < self.LIMIT):
			
			self.page_count += 1
			# next_page = next_page.strip()
			# next_page = self.add_string_to_complete_url_if_needed(next_page, self.page_url)
			next_page = response.xpath(self.spider_config_flat[ "next_page" ]).extract_first()
		
			return True, next_page
		
		else:
			return False, next_page


	### clean a link if http is missing
	def clean_link(self, link=None):
		""" complete a link if needed """
		
		if not link.startswith("http"): 
			separator = ""
			if not link.startswith("/"):
				separator = "/"
			link 	= "{}{}{}".format( self.page_url, separator, link)			

		return link




	# def get_link(self, action, xpath=None, data_type="link"):
	# def get_link(self, raw_data, xpath=None) :
	# 	"""
	# 	Used to retrieve links.
	# 	If no xpath is given, will get the data for the Action's link attribute
	# 	"""
		
	# 	if xpath is None:
	# 		xpath = self.link_xpath
	# 	try:
	# 		link = raw_data.xpath(xpath).extract_first()
	# 		if link is not None:
	# 			link = self.add_string_to_complete_url_if_needed( link, page_url_root=None)
	# 		return link
		
	# 	except : 
	# 		log_scrap.error("... fucking error at : get_link !!! ")
	# 		return None

	# 	# except AttributeError as e:
	# 	# 	error = "Error <{}> on " \
	# 	# 			"{} item n <{}> " \
	# 	# 			"page <{}>".format(e, data_type, self.item_count, self.page_count)
	# 	# 	self.error_array.append(error)
	# 	# 	return None


	# def add_string_to_complete_url_if_needed(self, not_complete_url, page_url_root=None):
	# 	"""
	# 	adds the missing beggining part of an url with the '/' if needed
	# 	"""
	# 	log_scrap.warning("... add_string_to_complete_url_if_needed ... ")

	# 	if page_url_root is None:
	# 		page_url_root = self.page_url
		
	# 	if not not_complete_url.startswith("http"):

	# 		if not not_complete_url.startswith("/"):
	# 			not_complete_url = "{}{}".format(  "/", not_complete_url)
			
	# 		not_complete_url = "{}{}".format( page_url_root, not_complete_url )
		
	# 	return not_complete_url








	def add_string_to_complete_url_if_needed(self, not_complete_url, rest_of_url=None):
		"""adds the missing beggining part of an url with the '/' if needed"""
		if rest_of_url is None:
			rest_of_url = self.page_url
		if not not_complete_url.startswith("http"):
			if not not_complete_url.startswith("/"):
				not_complete_url = "{}{}".format("/", not_complete_url)
			not_complete_url = "{}{}".format(rest_of_url, not_complete_url)
		return not_complete_url





	### TO DO : generic functions linked with DATAMODEL_FIELDS_TYPES
	def clean_type_text(self, response) :
		"""
		for field_type : "text"
		"""
		value = ""
		return value

	def clean_type_tags(self, response) :
		"""
		for field_type : "tags"
		"""
		value = ""
		return value

	def clean_type_url(self, response) :
		"""
		for field_type : "url", "email"
		"""
		value = ""
		return value

	def clean_type_adress(self, response) : 
		"""
		for field_type : "adress"
		"""
		value = ""
		return value

	def clean_type_image(self, response) : 
		"""
		fields : "image"
		"""
		value = ""
		return value

	def clean_type_date(self, response) : 
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

	print 
	log_scrap.info("--- run_generic_spider / spider_id : %s ", spider_id )
	
	# !!! spider is launched from main.py level !!! 
	# all relative routes referring to this...
	log_scrap.info("--- run_generic_spider / os.getcwd() : %s ", os.getcwd()  )

	### flattening run_spider_config : from nested to flat dict 
	log_scrap.info("--- run_generic_spider / 'flattenSpiderConfig()' on 'run_spider_config' --> 'spider_config_flat' ..." )
	spider_config_flat = flattenSpiderConfig( run_spider_config )


	### settings for crawler
	# cf : https://hackernoon.com/how-to-crawl-the-web-politely-with-scrapy-15fbe489573d
	# gllobal settings for scrapy processes (see upper)
	log_scrap.info("--- run_generic_spider / BOT_NAME :       %s ", settings.get('BOT_NAME') ) 
	log_scrap.info("--- run_generic_spider / USER_AGENT :     %s ", settings.get('USER_AGENT') )
	log_scrap.info("--- run_generic_spider / ITEM_PIPELINES : %s ", settings.get('ITEM_PIPELINES').__dict__ )
	# specific settings for this scrapy process
	settings.set( "CURRENT_SPIDER_ID" 				, spider_id )
	settings.set( "DOWNLOAD_DELAY" 					, DOWNLOAD_DELAY )
	settings.set( "RANDOMIZE_DOWNLOAD_DELAY"		, RANDOMIZE_DOWNLOAD_DELAY )


	### initiating crawler process
	log_scrap.info("--- run_generic_spider / instanciate process ..." 	 )
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

	
	
	print "\n\n{}\n".format("> > > "*20)





#############################################
### cool snippets 

	### convert to class object
	# spider = globals()[spider]