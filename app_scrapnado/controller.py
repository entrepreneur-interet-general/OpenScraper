import pprint 

import tornado.web, tornado.template
from tornado import gen

### import app settings / infos 
from config.app_infos import app_infos, app_main_texts
from config.settings_example import MONGODB_COLL_CONTRIBUTORS, MONGODB_COLL_DATAMODEL, MONGODB_COLL_DATASCRAPPED

### OpenScraper generic scraper
from scraper import run_generic_spider 

### import item classes
from scraper import GenericItem

########################
########################
### REQUEST HANDLERS ###
"""
Tornado supports any valid HTTP method (GET,POST,PUT,DELETE,HEAD,OPTIONS)
"""

########################
### Login handlers 

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("username")

class LoginHandler(BaseHandler):
	def get(self):
		self.render('login.html')
	def post(self):
		self.set_secure_cookie("username", self.get_argument("username"))
		self.redirect("/")
		
class WelcomeHandler(BaseHandler):
	"""
	handler for index page
	"""
	@tornado.web.authenticated
	def get(self):
		self.render(
			"index.html",
			page_title  = app_main_texts["main_title"],
			header_text = app_main_texts["main_header"],
			user=self.current_user
		)

	# def write_error(self, status_code, **kwargs):
	# 	self.write("Gosh darnit, user! You caused a %d error." % status_code)

class LogoutHandler(BaseHandler):
	def get(self):
		if (self.get_argument("logout", None)):
			self.clear_cookie("username")
			self.redirect("/")
 

########################
### lists / edit handlers

# class ContributorEditHandler(tornado.web.RequestHandler):
class ContributorEditHandler(BaseHandler):
	"""
	contributor edit handler
	"""
	def get(self, isbn=None):
		contributor = dict()
		if isbn:
			coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] # .books
			contributor = coll.find_one({"isbn": isbn})

		self.render("contributor_edit.html",
			page_title="CIS contributors",
			header_text="Edit contributor",
			contributor=contributor)

	def post(self, isbn=None):
		import time
		book_fields = [	'isbn', 'title', 'subtitle', 'image', 'author',
						'date_released', 'description']
		coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] # .books
		contributor = dict()
		if isbn:
			contributor = coll.find_one({"isbn": isbn})
		for key in book_fields:
			contributor[key] = self.get_argument(key, None)

		if isbn:
			coll.save(contributor)
		else:
			contributor['date_added'] = int(time.time())
			coll.insert_one(contributor)
		self.redirect("/recommended/")

# class ContributorsHandler(tornado.web.RequestHandler):
class ContributorsHandler(BaseHandler):
	"""
	list all contributors
	"""
	def get(self):
		coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] #db.contributors
		contributors = coll.find()
		self.render(
			"list_contributors.html",
			page_title = "List of contributors to CIS",
			header_text = "...",
			contributors = contributors
		)


########################
### run spider handlers

test_data_model = [
	
	# item contents
	"title", 
	"img", 
	"abstract", 
	"tags", # keywords

	# item source and
	"link_data", 
	"link_src", 
	"link_to",

	# item 
	"area",
	"adress",

	# item metadata 
	"author",
	"date_data",
	"item_created_at",

 	### for debugging purposes
	"testClass"
]



test_spider_config = {

	### mandatory fields
	"name"  : "TEST", 
	"label" : "test_spider_config",
	"page_url" : "http://quote.toscrape.com", # base url (ex : "https://www.mysite.org")
	"start_urls" : [ # List of URLs that will be crawled by the parse method
		'http://quotes.toscrape.com/'
	],

	### notes
	"notes" : u"test configuration for debugging / developping purposes...",

	### settings and logging fields
	"error_array" : [],
	"item_count": 0, # will be incremented each time a new item is created
	"item_count_depth_1" : 0,# will be incremented each time an item is completed in detailed page
	"LIMIT" : 3, # The number of pages where the spider will stop
	"page_count" : 1, # The number of pages already scraped
	"download_delay" : 0, # The delay in seconds between each request. some website will block too many requests

	### custom boolean on whether the page contains complete items or need to follow links
	"page_lists_full_items" : False, 

	### custom xpaths for next_page, filled by user
	"next_page_xpath" :'//li[@class="next"]/a/@href', 
	# "action_xpath" : "",  

	### custom xpaths for item, filled by user
	"abstract_xpath" : './span[@class="text"]/text()',
	"author_xpath" : './/small[@class="author"]/text()',
	"tags_xpath" : './/div[@class="tags"]/a[@class="tag"]/text()',

} 


avise_spider_config = {
	
	### mandatory fields
	"name" : "avise",
	"label" : "Avise",

	"page_url" : "http://www.avise.org",
	"start_urls" : ['http://www.avise.org/portraits', ],

	### notes
	"notes" : u"test configuration for debugging / developping purposes...",

	### settings and logging fields
	"error_array" : [],
	"item_count": 0, # will be incremented each time a new item is created
	"item_count_depth_1" : 0,# will be incremented each time an item is completed in detailed page
	"LIMIT" : 1, # The number of pages where the spider will stop
	"page_count" : 1, # The number of pages already scraped
	"download_delay" : 0, # The delay in seconds between each request. some website will block too many requests

	"list_xpath_selector" : '//div[@class:"view-content"]//div[@onclick]',
	"next_page_xpath" : '//li[@class:"pager-next"]/a/@href',

	# 
	"img_xpath" : './/image/@*[name():"xlink:href"]',
	"link_xpath" : './/h2/a/@href',
	"abstract_xpath" : './/div[@class:"field-item even"]/text()',
	"title_xpath" : './/h2/a/text()',

	# In action page
	"date_xpath" : 	'//div[@class:"field field--name-field-created-year field--type-text field--label-inline ' \
				 	'clearfix"]//div[@class:"field-item even"]/text()',
	"area_xpath" : 	'//div[@class:"addressfield-container-inline locality-block country-FR' \
				 	'"]/span/text()',
	"key_words_xpath" : '//div[@class:"field field--name-field-portrait-domain ' \
					  'field--type-text field--label-inline clearfix"]' \
					  '//div[@class:"field-item even"]//text()',
	"contact_xpath" : '//div[@id:"node-portrait-full-group-portrait-coordonnees"]//text()',
	"video_xpath" : "",
	"state_xpath" : "",
	"project_holder_xpath" : '//div[@id:"node-portrait-full-group-portrait-coordonnees"]' \
							 '//div[@class:"name-block"]/text()',
	"partner_xpath" : "",
	"economic_xpath" : "",
}


# class SpiderHandler(tornado.web.RequestHandler) : 
class SpiderHandler(BaseHandler) : 
	"""
	launch the run spider from client side and from url arg
	"""
	@tornado.web.authenticated
	@gen.coroutine
	def get(self, spidername = None ):
		
		print "\nSpiderHandler.get... "

		### retrieve spider config from its name in the db
		coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] #.contributors
		spider_config = coll.find_one({"name": spidername})
		
		### redirect / set default runner if no spider_config
		if spider_config == None : 
			print "SpiderHandler.get --- !!! Spidername not found : test spider with test_config"
			# test_config = {
			# 		"name"  : "quote", 
			# 		"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],
			# 	 } 
			# (this will come from DB later)
			spider_config = test_spider_config
		
		print "SpiderHandler.get --- spidername : ", spidername
		print "SpiderHandler.get --- spider_config :", spider_config

		print "SpiderHandler.get --- starting spider runner --- "
		### TO DO : CHECK IF REALLY WORKING : asynchronous run the corresponding spider
		# run_generic_spider( run_spider_config = spider_config ) # synchronous
		yield self.run_spider( spidername, spider_config=spider_config ) # asynchronous

		### TO DO : redirect to a page showing crawling status / results
		# self.redirect("/contributors/")
		self.render(
			"index.html",
			page_title = app_main_texts["main_title"],
			header_text = "crawling of -%s- launched ..." %(spidername),
			user = self.current_user
		)

	@gen.coroutine
	def run_spider (self, spidername, spider_config) :
		print "\nSpiderHandler.run_spider --- "

		print "SpiderHandler.run_spider --- creating scrapy custom_item "
		### getting data_model list (this will come from DB later)
		# coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]
		# data_model = coll_model.find_one({"name": yourdatamodel_name })
		data_model = test_data_model 

		### run spider 
		result = run_generic_spider( 
									spidername=spidername, 
									datamodel=data_model, 
									run_spider_config=spider_config 
									)
		raise gen.Return(result)


########################
########################
### TORNADO MODULES

class ContributorModule(tornado.web.UIModule):
	"""
	module for each contributor
	"""
	def render(self, contributor):
		return self.render_string(
			"modules/mod_contributor.html", 
			book=contributor,
		)
	
	def css_files(self):
		return "css/recommended.css"
	
	def javascript_files(self):
		return "js/recommended.js"