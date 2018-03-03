#!/usr/bin/env python

"""
OpenScrapper - a Tornado Scrapy spiders manager
------------------ 
a project by ... 

"""


### global imports
import os, os.path
import json
import datetime
from uuid import uuid4
import pprint

### tornado imports
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.options
import tornado.gen
# from tornado import httpclient, gen, ioloop, queues
from tornado.options import define, options
from tornado.concurrent import Future

### import app settings from .config.settings (keep that file confidential)
from config.settings_corefields import * 
from config.settings_example import * 
# from config.settings import * 

define( "port", default=APP_PORT, help="run on the given port", type=int )

# BDD imports and client
# import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne


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


### main Tornado application wrapper
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

		### connect to MongoDB
		client = MongoClient(
					host = MONGODB_HOST, 
					port = MONGODB_PORT
		)
		self.db = client[ MONGODB_DB ]

		### instantiate db.datamodel with core fields (for internal use)
		core_fields = [ 
			{ 	"field_name" 	: field["field_name"], 
				"field_type" 	: field["field_type"],
				"field_class" 	: "core" ,
				"added_by" 		: "admin"
			} for field in DATAMODEL_CORE_FIELDS
		]
		print "\n>>> Application.__init__ / datamodel - core_fields : ", 
		pprint.pprint(core_fields)
		
		# upsert fields as bulk job in mongoDB
		# cf : https://stackoverflow.com/questions/5292370/fast-or-bulk-upsert-in-pymongo
		operations =[ UpdateOne( 
			{"field_name" : field["field_name"]},
			{'$set':  { 
					"field_type" 	: field["field_type"],
					"field_class" 	: field["field_class"],
					"added_by" 		: field["added_by"],
					 } 
			}, 
			upsert=True ) for field in core_fields 
		]
		# self.db[ "test_coll" ].bulk_write(operations)
		self.db[ MONGODB_COLL_DATAMODEL ].bulk_write(operations)

		

		### retrieve handlers from urls.py
		handlers = urls.urls

		### basic app settings
		settings = dict(
			template_path	= os.path.join(os.path.dirname(__file__), "templates"),
			static_path		= os.path.join(os.path.dirname(__file__), "static"),
			ui_modules		= {
				"Contributor": ContributorModule,
			},

			login_url="/login",

			debug 			= APP_DEBUG ,
			cookie_secret 	= COOKIE_SECRET , ### example / store real key in ignored config.py
			xsrf_cookies  	= XSRF_ENABLED
		)
		
		### app init
		tornado.web.Application.__init__(self, handlers, **settings )



def main():
	"""
	start / run app
	"""
	print "\n>>> MAIN / STARTING SERVER ... >>>"

	tornado.options.parse_command_line()
	
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
	
	# http_server.bind(options.port)
	# http_server.start(0)  # Forks multiple sub-processes
	# tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
	main()
