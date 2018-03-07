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
	
	def __init__(self):
		print "\n>>> MongodbPipeline / __init__ ..."

	@classmethod
	def from_crawler(cls, crawler):
		print "\n>>> MongodbPipeline / classmethod ..."
		pipeline = cls()
		# crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		# crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline

	def process_item(self, item, spider):
		print ">>> MongodbPipeline / process_item ..."

		# check if already exists in db
		
		# insert / update in db

		return item

