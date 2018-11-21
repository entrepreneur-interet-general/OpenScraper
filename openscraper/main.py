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
import  csv
import 	datetime
from 	uuid import uuid4
import 	pprint
from 	pprint import pformat
import 	time
from datetime import datetime
# import random

from 	bson import json_util
from	bson.json_util import dumps

import argparse

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
# from config.settings_example import * 
# from config.settings import * 

from config.settings_secret import *



### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### SETUP LOGGERS with custom format
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
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
	print()
	app_log.info('>>> this is app_log ')
	gen_log.info('>>> this is gen_log ')
	access_log.info('>>> this is access_log ')
	print()


setup_loggers()


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### scrapy dependencies

# from scrapy.crawler import CrawlerRunner
# from scraper import *
# crawl_runner = CrawlerRunner()      # requires the Twisted reactor to run

### import dependencies

### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
# ### import controller : url functions

import urls
from controller import *

### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###


### snippet DB
# update/upsert a field for all documents in a collection
# cf : db.getCollection('contributors').update({}, {$set:{"infos.added_by" : "admin"} }, {upsert:true, multi:true})


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### DEFAULT VALUES AT MAIN LEVEL ############################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###


# # define default port to listen to + mode
define( "port", default=APP_PORT, help="run on the given port", type=int )
define( "mode", default='default', help="mode for run : default, production", type=str )



### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### UTILS AT MAIN LEVEL #####################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

'''
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


### setup loggers with custom format
setup_loggers()
'''

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

	logger.warning("... create_datamodel_fields / datamodel - fields_ : ")

	# upsert fields as bulk job in mongoDB
	# cf : https://stackoverflow.com/questions/5292370/fast-or-bulk-upsert-in-pymongo
	operations =[ UpdateOne( 
		{"field_name" : field["field_name"]},
		{'$set':  { 
				k : v for k,v in field.iteritems() if k != "field_name" 
				} 
		}, 
		upsert=True  # do not upsert otherwise if yo don't want new fields to be created
		) 
		for field in fields_ 
	]
	coll_model.bulk_write(operations)



def reset_is_running_on_all_spider( coll_model ) :
	"""
	reset is_running on all spiders to avoid errors if app shut down while one spider was running 
	"""

	print ()

	app_log.warning('>>> reset_is_running_on_all_spider ... ')
	
	# find if any spider was running
	running_spiders = coll_model.find({"scraper_log.is_running" : True})
	app_log.info(">>> running_spiders : \n %s" , list(running_spiders) )

	coll_model.update_many({'scraper_log.is_running' : True }, {"$set": {'scraper_log.is_running' : False }})

	# if list(running_spiders) != [] : 

	# 	app_log.warning('>>> reset_is_running_on_all_spider / some spiders were blocked in is_running == True ... ')
	# 	app_log.warning('>>> spiders are : \n %s', pformat(list(running_spiders)) )

	# 	coll_model.update({"scraper_log.is_running":True}, {"$set" : {"scraper_log.is_running" : False }})
	
	# print 


def backup_mongo_collection(coll, filepath) :
	"""
	dumps all documents in collection in _backups_collections 
	"""

	app_log.warning('>>> backup_mongo_collection ... ')

	cursor 		= coll.find({})
	backup_file = open(filepath, "w")
	backup_file.write('[')
	for document in cursor:
		backup_file.write(json.dumps(document,indent=4, default=json_util.default))
		backup_file.write(',')
	backup_file.write(']')

### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###


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
	
	def __init__(self, mode="default"):  


		timestamp = time.time()

		# ### setup loggers with custom format
		# setup_loggers()

		app_log.info('>>> Application.__init__ ... ')

		### check if default or production mode to load secret keys and app settings
		if mode=="production" : 
			try : 
				from config.settings_secret import *
			except :
				pass
		app_log.info(">>> WTF_CSRF_SECRET_KEY 	: %s ", WTF_CSRF_SECRET_KEY)
		app_log.info(">>> JWT_SECRET_KEY 		: %s ", JWT_SECRET_KEY)


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

		# create default fields in spiders collection in case fields are missing
		self.coll_spiders.update_many({'infos.logo_url'						: {"$exists" : False}}, {"$set": {'infos.logo_url' 	: "" }})
		self.coll_spiders.update_many({'infos.licence'						: {"$exists" : False}}, {"$set": {'infos.licence' 	: "" }})

		self.coll_spiders.update_many({'scraper_config.parse_reactive'		: {"$exists" : False}}, {"$set": {'scraper_config.parse_reactive' 		: False }})
		self.coll_spiders.update_many({'scraper_config.parse_api'			: {"$exists" : False}}, {"$set": {'scraper_config.parse_api' 			: False }})
		self.coll_spiders.update_many({'scraper_config.follow_is_api'		: {"$exists" : False}}, {"$set": {'scraper_config.follow_is_api' 		: False }})
		self.coll_spiders.update_many({'scraper_config.api_pagination_root'	: {"$exists" : False}}, {"$set": {'scraper_config.api_pagination_root' 	: "" }})
		self.coll_spiders.update_many({'scraper_config.api_follow_root'		: {"$exists" : False}}, {"$set": {'scraper_config.api_follow_root' 		: "" }})
		
		self.coll_spiders.update_many({'scraper_config.deploy_list'			: {"$exists" : False}}, {"$set": {'scraper_config.deploy_list' 			: False }})
		self.coll_spiders.update_many({'scraper_config.deploy_list_xpath'	: {"$exists" : False}}, {"$set": {'scraper_config.deploy_list_xpath' 	: "" }})

		# self.coll_spiders.update_many({'scraper_settings.download_delay'		: {"$exists" : False}}, {"$set": {'scraper_settings.download_delay' : 0.25 }})
		self.coll_spiders.update_many({'scraper_settings.RETRY_TIMES'			: {"$exists" : False}}, {"$set": {'scraper_settings.RETRY_TIMES' 		: 3 }})
		self.coll_spiders.update_many({'scraper_settings.LIMIT_ITEMS'			: {"$exists" : False}}, {"$set": {'scraper_settings.LIMIT_ITEMS' 		: 0 }})
		self.coll_spiders.update_many({'scraper_settings.LIMIT_PAGES'			: {"$exists" : False}}, {"$set": {'scraper_settings.LIMIT_PAGES'		: 100 }})
		self.coll_spiders.update_many({'scraper_settings.CONCURRENT_ITEMS'		: {"$exists" : False}}, {"$set": {'scraper_settings.CONCURRENT_ITEMS'	: 200 }})
		self.coll_spiders.update_many({'scraper_settings.CONCURRENT_REQUESTS'	: {"$exists" : False}}, {"$set": {'scraper_settings.CONCURRENT_REQUESTS': 100 }})
		self.coll_spiders.update_many({'scraper_settings.wait_driver'			: {"$exists" : False}}, {"$set": {'scraper_settings.wait_driver' 		: 5.0 }})
		self.coll_spiders.update_many({'scraper_settings.wait_page'				: {"$exists" : False}}, {"$set": {'scraper_settings.wait_page' 			: 1.5 }})
		self.coll_spiders.update_many({'scraper_settings.wait_implicit'			: {"$exists" : False}}, {"$set": {'scraper_settings.wait_implicit' 		: 0.5 }})
		
		self.coll_spiders.update_many({'scraper_settings.RANDOMIZE_DOWNLOAD_DELAY' 	: {"$exists" : False}}, {"$set": {'scraper_settings.RANDOMIZE_DOWNLOAD_DELAY' 	: True }})
		self.coll_spiders.update_many({'scraper_settings.HTTPCACHE_ENABLED' 		: {"$exists" : False}}, {"$set": {'scraper_settings.HTTPCACHE_ENABLED' 			: True }})
		self.coll_spiders.update_many({'scraper_settings.AUTOTHROTTLE_ENABLED' 		: {"$exists" : False}}, {"$set": {'scraper_settings.AUTOTHROTTLE_ENABLED' 		: False }})
		self.coll_spiders.update_many({'scraper_settings.ROBOTSTXT_OBEY' 			: {"$exists" : False}}, {"$set": {'scraper_settings.ROBOTSTXT_OBEY' 			: False }})
		self.coll_spiders.update_many({'scraper_settings.BOT_NAME' 					: {"$exists" : False}}, {"$set": {'scraper_settings.BOT_NAME' 					: "OpenScraper" }})
		self.coll_spiders.update_many({'scraper_settings.USER_AGENT' 				: {"$exists" : False}}, {"$set": {'scraper_settings.USER_AGENT' 				: "Open Scraper (+https://github.com/entrepreneur-interet-general/OpenScraper)" }})


		# create index for every collection needing it  
		# cf : https://code.tutsplus.com/tutorials/full-text-search-in-mongodb--cms-24835 
		self.coll_spiders.create_index([('$**', 'text')])
		self.coll_data.create_index([('$**', 'text')])
		# TO DO 
		# then create an index for all fields in custom fields, especially tags
		# 

		app_log.info("self.coll_data.index_information() : \n %s ", pformat(self.coll_data.index_information() ) )



		### instantiate db.datamodel with core fields (for internal use) if no core field at all in db
		existing_core_fields = self.coll_model.find({"field_class" : "core"})
		app_log.warning("existing_core_fields.count() : %s", existing_core_fields.count())
		if existing_core_fields.count() == 0 : 
			app_log.warning("no core fields... creating default core fields...")
			create_datamodel_fields( app_log, self.coll_model, DATAMODEL_CORE_FIELDS, "core" )

		### instanciate default custom fields if no custom field at all in db
		existing_custom_fields = self.coll_model.find({"field_class" : "custom"})
		app_log.warning("existing_custom_fields.count() : %s", existing_custom_fields.count())
		# if list(existing_custom_fields) == [] : 
		if existing_custom_fields.count() == 0 : 
			app_log.warning("no custom fields... creating default custom fields...")
			create_datamodel_fields( app_log, self.coll_model, DATAMODEL_DEFAULT_CUSTOM_FIELDS, "custom" )


		### instanciate default spider if no custom field at all in db
		existing_spiders = self.coll_spiders.find({})
		app_log.warning("existing_spiders.count() : %s", existing_spiders.count())
		if existing_spiders.count() == 0 : 
			app_log.warning("no spiders neither custom fields... creating one default spider...")
			
			from scraper.default_test_spider import create_default_spider
			try : 
				create_default_spider( self.coll_model, self.coll_spiders ) 
			except : 
				app_log.error("enable to create a default spider...")


		### reset spiders scrape_log.is_running
		reset_is_running_on_all_spider( self.coll_spiders )


		### BACKUPS / TEMPORARY SOLUTION : backup all spiders and users collections to JSON
		# backup all collections when restart in ./_backups_collections
		cwd = os.getcwd()
		app_log.info('>>> BACKUP MONGO COLLECITONS : cwd : %s', cwd )
		reboot_datetime = datetime.now().strftime("%Y-%m-%d-h%H-m%M-s%S")
		backup_mongo_collection(self.coll_spiders,	 cwd + "/_backups_collections/backup_coll_spiders-"+reboot_datetime +".json")
		backup_mongo_collection(self.coll_model,	 cwd + "/_backups_collections/backup_coll_model-"+reboot_datetime +".json")
		backup_mongo_collection(self.coll_users,	 cwd + "/_backups_collections/backup_coll_users-"+reboot_datetime +".json")



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

			autoreload 		= APP_AUTORELOAD,

			debug 			= APP_DEBUG ,
			cookie_secret 	= WTF_CSRF_SECRET_KEY , ### example / store real key in ignored config.settings_secret.py
			xsrf_cookies  	= XSRF_ENABLED
		)

		
		### app init
		tornado.web.Application.__init__(self, handlers, **settings )
		app_log.info (">>> Application.__init__ end ... \n")




def main():
	"""
	start / run app
	"""

	### setup loggers with custom format
	# setup_loggers()

	print()
	print( "{}".format("+ + + "*20))
	gen_log.warning( ">>> MAIN / RE-STARTING SERVER ... >>>\n")

	# printing current IP adress
	import socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip_adress = s.getsockname()
	app_log.info(">>> IP_ADRESS IS : %s ", ip_adress[0] )
	s.close()

	# parse command line arguments if any port arg
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--port', type=int, default=APP_PORT)
	parser.add_argument('-m', '--mode', type=str, default="default")
	args = parser.parse_args()

	# update port with args.port
	options.port = args.port
	options.mode = args.mode

	# set os environment variable for mode
	os.environ['APP_MODE'] = str(options.mode)

	app_log.info(">>> ARG.PORT FROM COMMAND LINE : %s ", args.port)
	app_log.info(">>> ARG.MODE FROM COMMAND LINE : %s ", args.mode)

	# read optionnal args from command line
	# tornado.options.parse_command_line()
	app_log.info(">>> options.__dict__ : \n%s", pformat(options.__dict__))

	# print port for reminder
	app_log.info( ">>> starting tornado / options.port    : %s ", options.port)
	app_log.info( ">>> starting tornado / options.logging : %s ", options.logging)
	app_log.info( ">>> starting tornado / options.help    : %s ", options.help)
	app_log.info( ">>> starting tornado / options.mode    : %s ", options.mode)


	# ### import dependencies
	# import urls

	### import controller : url functions
	# from controller import *


	# create server with args.mode
	http_server = tornado.httpserver.HTTPServer(Application( mode=args.mode ))
	app_log.info( ">>> http_server ready ...")


	# for local dev --> debug
	if APP_DEBUG == True : 
		http_server.listen(options.port)
		tornado.ioloop.IOLoop.instance().start()

	# for prod --> doesn't work with autoreload == True
	# cf : http://www.tornadoweb.org/en/stable/guide/running.html
	elif APP_DEBUG == False : 
		http_server.bind(options.port)	
		http_server.start(0)  			# forks one process per cpu
		tornado.ioloop.IOLoop.current().start()

	print ("\n{}\n".format("+ + + "*20))




if __name__ == "__main__":

	main()
