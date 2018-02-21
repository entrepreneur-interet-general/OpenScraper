#!/usr/bin/env python

"""
CIS SPIDER MANAGER
------------------ 
a project by ... 

"""


### global imports
import os
import json

### tornado imports
import tornado.ioloop
import tornado.web
# from tornado import httpclient, gen, ioloop, queues
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

### import dependencies
import urls

### BDD imports and client
# import pymongo
from pymongo import MongoClient


### scrapy dependencies
from scrapy.crawler import CrawlerRunner
from scraper import *
crawl_runner = CrawlerRunner()      # requires the Twisted reactor to run

### import controller : url functions
from controller import *


### main application wrapper
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

		### scrapy init


		### connect to MongoDB
		client = MongoClient(host='localhost', port=27017) # MongoClient()
		self.db = client.bookstore

		### retrieve handlers from urls.py
		handlers = urls.urls

		### basic app settings
		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			ui_modules={"Book": ContributorModule},
			debug=True,
		)
		
		### app init
		tornado.web.Application.__init__(self, handlers, **settings )



def main():
	"""
	start / run app
	"""
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
