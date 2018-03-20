#!/usr/bin/env python

"""
OpenScrapper - a Tornado Scrapy spiders manager
------------------ 
a project by ... 

"""


### global imports
import 	os, os.path
import 	sys
import 	json
import 	datetime
from 	uuid import uuid4
import 	pprint

# BDD imports and client
# import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne


### tornado imports
# from 	tornado.ioloop import IOLoop
import 	tornado.web
import 	tornado.auth
import 	tornado.options
import 	tornado.gen
# from tornado import httpclient, gen, ioloop, queues
from tornado.options import define, options
# from tornado.concurrent import Future


### import logger
# cf : http://www.patricksoftwareblog.com/python-logging-tutorial/
# cf : https://gitlab.com/patkennedy79/python_logging/blob/master/python_logging/__init__.py
# cf : http://docs.python-guide.org/en/latest/writing/logging/ 
from 	os import path, remove
import 	logging
import 	logging.config
from 	logging.config import dictConfig
from 	config.settings_logging import logging_config

from 	tornado.log import enable_pretty_logging, LogFormatter, access_log, app_log, gen_log



### import app settings from .config.settings (keep that file confidential)
from config.settings_corefields import * 
from config.settings_example import * 
# from config.settings import * 

define( "port", default=APP_PORT, help="run on the given port", type=int )



### scrapy dependencies
# from scrapy.crawler import CrawlerRunner
from scraper import *
# crawl_runner = CrawlerRunner()      # requires the Twisted reactor to run

### import dependencies
import urls

### import controller : url functions
from controller import *


### snippet DB
# update/upsert a field for all documents in a collection
# cf : db.getCollection('contributors').update({}, {$set:{"infos.added_by" : "admin"} }, {upsert:true, multi:true})


### UTILS AT MAIN LEVEL
def create_datamodel_fields( logger, coll_model, fields_list, field_class ) : 
	"""
	create datamodel fields from list of field basic dict like DATAMODEL_CORE_FIELDS
	"""

	timestamp = time.time()

	if field_class == "core":
		is_visible = False
	if field_class == "custom":
		is_visible = True
		

	### instantiate db.datamodel with core fields (for internal use)
	fields_ = [ 
		{ 	"field_name" 	: field["field_name"], 
			"field_type" 	: field["field_type"],
			"field_open" 	: field["field_open"],
			"field_class" 	: field_class ,
			"added_by" 		: "admin",
			"added_at"		: timestamp,
			"is_visible"	: is_visible
		} for field in fields_list
	]

	logger.info("... create_datamodel_fields / datamodel - fields_ : ")
	# pprint.pprint(fields_)

	# upsert fields as bulk job in mongoDB
	# cf : https://stackoverflow.com/questions/5292370/fast-or-bulk-upsert-in-pymongo
	operations =[ UpdateOne( 
		{"field_name" : field["field_name"]},
		{'$set':  { 
				k : v for k,v in field.iteritems() if k != "field_name" 
				} 
		}, 
		upsert=True ) for field in fields_ 
	]
	coll_model.bulk_write(operations)

def setup_loggers ():
	"""
	set up tornado loggers with custom format
	
	logger has 5 severity levels : 
		D - DEBUG (lowest)
		I - INFO
		W - WARNING
		E - ERROR
		C - CRITICAL (highest)
	"""

	# config logger output in console
	# logging.basicConfig(	level 	= logging.DEBUG, 
	# 						format 	= "%(name)s - %(funcName)s - %(levelname)s : %(message)s" )

	# Create a Formatter for formatting the log messages
	# log_formatter = logging.Formatter('%(name)s -- %(funcName)s - %(levelname)s - %(message)s')
	openscraper_log_format = '%(color)s::: %(levelname)s %(name)s %(asctime)s ::: %(module)s:%(lineno)d -in- %(funcName)s() :::%(end_color)s \
		%(message)s' 
	# datefmt='%y%m%d %H:%M:%S'
	# style='%'
	# color=True
	# colors={40: 1, 10: 4, 20: 2, 30: 3}
	"""	
	default tornado format for logging : 
		fmt='%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
		datefmt='%y%m%d %H:%M:%S'
		style='%'
		color=True
		colors={40: 1, 10: 4, 20: 2, 30: 3}
		))
	"""
	# log_formatter = logging.Formatter( fmt=openscraper_log_format )
	tornado_log_formatter = LogFormatter(fmt=openscraper_log_format, color=True)

	enable_pretty_logging()

	### Logger as self var
	# create the Logger
	# dictConfig(logging_config)
	# self.log 		= logging.getLogger(__name__)
	# self.logger 	= logging.getLogger()
	# self.access_log = logging.getLogger("tornado.access")
	# self.app_log 	= logging.getLogger("tornado.application")
	# self.gen_log 	= logging.getLogger("tornado.general")

	### Get root logger
	root_logger 	= logging.getLogger()
	# print root_logger.__dict__

	### Format root_logger stream
	# parent_logger = app_log.parent
	# print parent_logger.__dict__
	# root_stream_handler = parent_logger.handlers
	# root_stream_handler[0].setFormatter(tornado_log_formatter)
	root_logger.handlers[0].setFormatter(tornado_log_formatter)

	# streamHandler 	= logging.StreamHandler() # stream=sys.stdout
	# streamHandler.setFormatter(tornado_log_formatter)
	# self.gen_log.addHandler(streamHandler)
	# self.app_log.addHandler(streamHandler)
	# self.access_log.addHandler(streamHandler)

	# self.log.setLevel(logging.DEBUG)



	# Create the Handlers for logging data to log files
	gen_log_handler 	= logging.FileHandler('logs/openscraper_general.log')
	gen_log_handler.setLevel(logging.WARNING)

	access_log_handler 	= logging.FileHandler('logs/openscraper_access.log')
	access_log_handler.setLevel(logging.WARNING)

	app_log_handler 	= logging.FileHandler('logs/openscraper_app.log')
	app_log_handler.setLevel(logging.WARNING)

	# Add the Formatter to the Handler
	gen_log_handler.setFormatter(tornado_log_formatter)
	access_log_handler.setFormatter(tornado_log_formatter)
	app_log_handler.setFormatter(tornado_log_formatter)


	# Add the Handler to the Logger
	gen_log.addHandler(gen_log_handler)
	access_log.addHandler(access_log_handler)	
	app_log.addHandler(app_log_handler)	
	
	# test loggers
	print
	app_log.info('>>> this is app_log ')
	gen_log.info('>>> this is gen_log ')
	access_log.info('>>> this is access-log ')
	print 


### MAIN TORNADO APPLICATION WRAPPER
class Application(tornado.web.Application):
	"""
	main Tornado application wrapper :
		- set MongoDB client
		- set scrapy
		- set modules
		- set urls handlers
		- set and init Tornado app
	"""
	
	def __init__(self):  


		timestamp = time.time()

		### setup loggers with custom format
		setup_loggers()

		app_log.info('>>> Application.__init__ ... ')

		### connect to MongoDB with variables from config.settings.py
		client = MongoClient(
					host = MONGODB_HOST, 
					port = MONGODB_PORT
		)
		self.db = client[ MONGODB_DB ]
		

		# predefine collection names as .self objects
		self.coll_users 	= self.db[ MONGODB_COLL_USERS ]
		self.coll_model 	= self.db[ MONGODB_COLL_DATAMODEL ]
		self.coll_spiders 	= self.db[ MONGODB_COLL_CONTRIBUTORS ]
		self.coll_data		= self.db[ MONGODB_COLL_DATASCRAPPED ]

		### instantiate db.datamodel with core fields (for internal use)
		# core_fields = [ 
		# 	{ 	"field_name" 	: field["field_name"], 
		# 		"field_type" 	: field["field_type"],
		# 		"field_class" 	: "core" ,
		# 		"added_by" 		: "admin",
		# 		"added_at"		: timestamp,
		# 		"is_visible"	: False
		# 	} for field in DATAMODEL_CORE_FIELDS
		# ]
		# print ">>> Application.__init__ / datamodel - core_fields : "
		# pprint.pprint(core_fields)

		# upsert fields as bulk job in mongoDB
		# cf : https://stackoverflow.com/questions/5292370/fast-or-bulk-upsert-in-pymongo
		# operations =[ UpdateOne( 
		# 	{"field_name" : field["field_name"]},
		# 	{'$set':  { 
		# 			"field_type" 	: field["field_type"],
		# 			"field_class" 	: field["field_class"],
		# 			"added_by" 		: field["added_by"], 	# "admin",
		# 			"added_at" 		: field["added_at"], 	# timestamp,
		# 			"is_visible"	: field["is_visible"], 	# False
		# 			} 
		# 	}, 
		# 	upsert=True ) for field in core_fields 
		# ]
		# self.coll_model.bulk_write(operations)
		create_datamodel_fields( app_log, self.coll_model, DATAMODEL_CORE_FIELDS, "core" )

		### instantiate core and default custom fields if no custom field at all in db
		existing_custom_fields = self.coll_model.find({"field_type" : "custom"})
		if existing_custom_fields == None : 
			create_datamodel_fields( self.coll_model, DATAMODEL_DEFAULT_CUSTOM_FIELDS, "custom" )

		### retrieve handlers from urls.py
		handlers = urls.urls

		### basic app settings
		settings = dict(
			template_path	= os.path.join(os.path.dirname(__file__), "templates"),
			static_path		= os.path.join(os.path.dirname(__file__), "static"),
			ui_modules		= {
				# "Contributor"	: ContributorModule,
				"Pagination"	: PaginationModule,
				"MainTabs"		: MainTabsModule,
				"ErrorModal"	: ErrorModalModule
			},

			login_url		= "/login/",

			debug 			= APP_DEBUG ,
			cookie_secret 	= COOKIE_SECRET , ### example / store real key in ignored config.py
			xsrf_cookies  	= XSRF_ENABLED
		)
		
		### app init
		tornado.web.Application.__init__(self, handlers, **settings )
		app_log.info (">>> Application.__init__ end ... \n")




def main():
	"""
	start / run app
	"""

	print "\n\n{}".format("+ + + "*20)
	print "\n\n>>> MAIN / RE-STARTING SERVER ... >>>\n"

	tornado.options.parse_command_line()

	app_log.info( ">>> starting app ...")
	
	http_server = tornado.httpserver.HTTPServer(Application())
	app_log.info( ">>> http_server ready ...")

	http_server.listen(options.port)
	
	print "\n{}\n".format("+ + + "*20)

	tornado.ioloop.IOLoop.instance().start()


	# ioloop = IOLoop.instance()
	# ioloop.start()
	
	# http_server.bind(options.port)
	# http_server.start(0)  # Forks multiple sub-processes
	# tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
	main()
