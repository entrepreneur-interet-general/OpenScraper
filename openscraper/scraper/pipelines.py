# -*- encoding: utf-8 -*-

import json 

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
	

	def __init__(self, mongo_uri=None, mongo_db=None):

		print "\n>>> MongodbPipeline / __init__ ..."
		self.mongo_db	= mongo_db
		self.mongo_uri	= mongo_uri

	
	@classmethod
	def from_crawler(cls, crawler):
		
		print "\n>>> MongodbPipeline / classmethod ..."
		
		## pull in information from settings.py

		pipeline = cls(
			mongo_uri	=	crawler.settings.get('MONGO_URI'),
			mongo_db	=	crawler.settings.get('MONGO_DATABASE')
		)
		# crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		# crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline
		# return cls()



	def process_item(self, item, spider):
		"""handle each item and post it to db"""

		print ">>> MongodbPipeline / process_item ..."

		# item object to dict
		item_dict = "test" # item.__dict__
		print ">>> MongodbPipeline / item_dict : ", item_dict

		# check if already exists in db
		# self.application.coll_data.find({})

		# insert / update in db
		# self.db[self.collection_name].insert(dict(item))

		return item