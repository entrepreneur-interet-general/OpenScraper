# -*- encoding: utf-8 -*-
import os
import json 
import pprint
import pymongo
from pymongo import MongoClient


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
	

	@classmethod
	def from_crawler(cls, crawler):
		
		print "\n>>> MongodbPipeline / @classmethod + from_crawler ..."
		
		## pull in information from settings.py
		pipeline = cls(
			mongo_uri			= crawler.settings.get('MONGO_URI'),
			mongo_db			= crawler.settings.get('MONGO_DATABASE'),
			mongo_coll_scrap 	= crawler.settings.get('MONGO_COLL_SCRAP')
		)
		# crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		# crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline # equivalent to : return cls(*args, **kwargs)

	def __init__(self, mongo_uri=None, mongo_db=None, mongo_coll_scrap=None):

		print "\n>>> MongodbPipeline / __init__ ..."
		# self.mongo_uri			= mongo_uri
		# self.mongo_db			= mongo_db
		# self.mongo_coll_scrap 	= mongo_coll_scrap
		print "--- MongodbPipeline / os.getcwd() : ", os.getcwd() 
		# client 	= MongoClient( 
		# 			mongo_uri
		# 			# host = MONGODB_HOST, 
		# 			# port = MONGODB_PORT
		# )
		# db 		= client[mongo_db]
		# self.coll_data = db[ mongo_coll_scrap ]

	def open_spider(self, spider):
		## initializing spider
		## opening db connection
		print "\n>>> MongodbPipeline / open_spider ..."

		# self.client = pymongo.MongoClient(self.mongo_uri)
		# self.db = self.client[self.mongo_db]
		pass

	def close_spider(self, spider) :
        ## clean up when spider is closed
		print "\n>>> MongodbPipeline / close_spider ..."
		pass
		
	def process_item(self, item, spider):
		"""handle each item and post it to db"""

		print "\n>>> MongodbPipeline / process_item ..."

		# item object to dict
		item_dict = dict(item)
		print ">>> MongodbPipeline / item_dict : "
		pprint.pprint(item_dict)

		# check if already exists in db
		# self.application.coll_data.find({})

		# insert / update in db
		# self.coll_data.insert(dict(item))

		return item