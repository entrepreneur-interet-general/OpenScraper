# -*- encoding: utf-8 -*-
import 	os
import 	json 
import 	pprint
import 	pymongo
from 	pymongo import MongoClient
from 	scrapy 	import signals


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
					spider_id=None,
					mongo_uri=None,
					mongo_db=None, 
					mongo_coll_scrap=None
					):

		print "\n>>> MongodbPipeline / __init__ ..."
		
		self.spider_id			= spider_id
		self.mongo_uri			= mongo_uri
		self.mongo_db			= mongo_db
		self.mongo_coll_scrap 	= mongo_coll_scrap
		
		print "--- MongodbPipeline / os.getcwd() : ", os.getcwd() 


	@classmethod
	def from_crawler(cls, crawler):
		
		print "\n>>> MongodbPipeline / @classmethod + from_crawler ..."
		
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
		## initializing spider

		print "\n>>> MongodbPipeline / open_spider ..."

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
		print "\n>>> MongodbPipeline / close_spider ..."
		self.client.close()


	def process_item(self, item, spider):
		"""handle each item and post it to db"""

		print "\n>>> MongodbPipeline / process_item ..."

		# item object to dict
		item_dict = dict(item)
		print ">>> MongodbPipeline / item_dict : "
		pprint.pprint(item_dict)

		# check if already exists in db
		# item_exists = self.application.coll_data.find({ "field_name" : item["field_name"]})

		# insert / update in db
		self.coll_data.insert(item_dict)

		return item