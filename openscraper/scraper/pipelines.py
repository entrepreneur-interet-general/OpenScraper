# -*- encoding: utf-8 -*-


from 	tornado.log import enable_pretty_logging, LogFormatter, access_log, app_log, gen_log

gen_log.info("---> importing .pipelines")

import 	os
import 	json 
from 	pprint import pprint, pformat
import 	pymongo
from 	pymongo import MongoClient
from 	scrapy 	import signals

import 	logging
from 	tornado.log import app_log, gen_log, access_log

# set logger for scrapy
log_pipe = logging.getLogger("log_pipeline")
log_pipe.setLevel(logging.DEBUG)

# Create the Handler for logging data to a file
logger_handler = logging.FileHandler('logs/openscraper_pipeline_logging.log')
logger_handler.setLevel(logging.WARNING)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
log_pipe.addHandler(logger_handler)
log_pipe.info('>>> Completed configuring log_pipe !')



# cf / sql : https://stackoverflow.com/questions/41043970/how-to-pass-parameter-to-a-scrapy-pipeline-object
# cf / mongodb : https://alysivji.github.io/mongodb-pipelines-in-scrapy.html

### TO DO 
# define a JSON writer pipeline
class JsonWriterPipeline(object):
	
	def __init__(self):
		self.file = open('items.jl', 'wb')

	def process_item(self, item, spider):
		line = json.dumps(dict(item)) + "\n"
		self.file.write(line)
	
		return item

### TO DO 
# define a Restexport pipeline
class RestExportPipeline(object):
	"""
	REST API writer pipeline
	"""
	pass
	# base_url = 'http://localhost:8000/'
	# base_url = 'https://social-connect-cget.herokuapp.com/'
	# token_file = open('token.env')
	# token = token_file.read().strip()
	# contributor_id = ""
	# geo_loc_getter = GeoCodingGetter()
	# logger = logging.getLogger(__name__)


# define a mongo pipeline
class MongodbPipeline(object):

	def __init__(	self, 
					spider_id	= None,
					mongo_uri	= None,
					mongo_db	= None, 
					mongo_coll_scrap = None
					):

		log_pipe.info(">>> MongodbPipeline / __init__ ...")
		
		self.spider_id			= spider_id
		self.mongo_uri			= mongo_uri
		self.mongo_db			= mongo_db
		self.mongo_coll_scrap 	= mongo_coll_scrap
		
		log_pipe.info("--- MongodbPipeline / os.getcwd() : %s \n", os.getcwd() )


	@classmethod
	def from_crawler(cls, crawler):
		
		log_pipe.debug(">>> MongodbPipeline / @classmethod + from_crawler ...\n")
		
		## pull in information from crawler.settings
		pipeline = cls(
			
			# global setting for crawler process : inherited from outside run_generic_spider
			mongo_uri			= crawler.settings.get('DB_DATA_URI'),
			mongo_db			= crawler.settings.get('DB_DATA_DATABASE'),
			mongo_coll_scrap 	= crawler.settings.get('DB_DATA_COLL_SCRAP'),
			
			# specific settings for crawler process : inherited from within run_generic_spider
			spider_id			= crawler.settings.get('CURRENT_SPIDER_ID')
			)
		# crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		# crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		
		# return the class itself
		return pipeline # equivalent to : return cls(*args, **kwargs)


	def open_spider(self, spider):
		"""" initializing spider """

		log_pipe.debug(">>> MongodbPipeline / open_spider ...\n")

		## opening db connection
		self.client 	= MongoClient( 
							self.mongo_uri
							# host = mongo_host, 
							# port = mongo_port
						)
		self.db 		= self.client[ self.mongo_db]
		self.coll_data  = self.db[ self.mongo_coll_scrap ]

		### remove all previous items scraped from same spider
		item_exists = self.coll_data.find({ "spider_id" : self.spider_id })
		if item_exists != None :
			self.coll_data.delete_many({ "spider_id" : self.spider_id })



	def close_spider(self, spider) :
		## clean up when spider is closed
		
		log_pipe.debug(">>> MongodbPipeline / close_spider ...\n\n")
		self.client.close()


	def process_item(self, item, spider):
		"""handle each item and post it to db"""

		print()
		log_pipe.debug(">>> MongodbPipeline / process_item ...")

		# item object to dict
		item_dict = dict(item)
		log_pipe.debug(">>> MongodbPipeline / process_item - item_dict : \n %s \n", pformat(item_dict) ) 


		# TO DO : for now all docs from this spider are wiped out at "open_spider" level 
		# check if already exists in db
		# item_exists = self.application.coll_data.find({ "field_name" : item["field_name"]})


		# insert / update in db
		self.coll_data.insert(item_dict)
		log_pipe.debug(">>> MongodbPipeline / process_item - item saved ...")

		return item