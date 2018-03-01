import pprint 
from bson import ObjectId

import tornado.web, tornado.template
from tornado import gen

### import app settings / infos 
from config.app_infos import app_infos, app_main_texts
from config.settings_example import MONGODB_COLL_CONTRIBUTORS, MONGODB_COLL_DATAMODEL, MONGODB_COLL_DATASCRAPPED
from config.settings_corefields import *

### import contributor generic class
from contributor import ContributorBaseClass

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
		print "this is the welcome page requested from url..."
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

class ContributorEditHandler(BaseHandler): #(tornado.web.RequestHandler):
	"""
	contributor edit handler
	"""
	def get(self, spidername=None):
		"""show infos on one contributor : get info in DB and prefill form"""

		print "\nContributorEditHandler.get ... "

		### retrieve datamodel custom
		coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]
		data_model = list(coll_model.find( {"field_class" : "custom"})) #, {"field_name":1, "_id":1} ))
		data_model = [ { k : str(v) for k,v in i.iteritems() } for i in data_model ]
		print "\n... ContributorEditHandler.get / data_model : "
		pprint.pprint(data_model)

		data_model_next_page = coll_model.find_one( {"field_name" : "next_page"}) #, {"field_name":1, "_id":1} )
		data_model_next_page = { k : str(v) for k,v in data_model_next_page.iteritems() }
		print "\n... ContributorEditHandler.get / data_model_next_page : "
		pprint.pprint(data_model_next_page)

		### retrieve contributor data from spidername
		# core empty contributor structure to begin with
		contributor = CONTRIBUTOR_CORE_FIELDS

		contributor_edit_fields = CONTRIBUTOR_EDIT_FIELDS
		print "\n... ContributorEditHandler.get / contributor_edit_fields :"
		pprint.pprint(contributor_edit_fields)

		if spidername:
			coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] 
			contributor = coll.find_one({"scraper_config.spidername": spidername})

		print "\n... ContributorEditHandler.get / contributor :"
		pprint.pprint(contributor)

		### render page
		self.render("contributor_edit.html",
			page_title 	= app_main_texts["main_title"],
			# header_text = "Edit contributor",
			contributor_edit_fields = contributor_edit_fields,
			contributor = contributor,
			datamodel	= data_model,
			datamodel_next_page	= data_model_next_page,
		)

	def post(self, spidername=None):
		"""update contributor in DB"""
		
		import time
		#####################################
		### TO DO : REAL UPDATE FOR CONTRIBUTOR 
		# #####################################
		# book_fields = [	'name', 'title', 'subtitle', 'image', 'author',
		# 				'date_released', 'description']

		# contributor = dict()
		contributor = CONTRIBUTOR_CORE_FIELDS
		
		coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] 
		if spidername:
			contributor = coll.find_one({"scraper_config.spidername": spidername})
		print "ContributorEditHandler.post / contributor :"
		pprint.pprint(contributor)
		
		for key in book_fields:
			contributor[ key ] = self.get_argument(key, None)

		if spidername:
			# coll.save(contributor)
			pass
		else:
			# contributor['date_added'] = int(time.time())
			coll.insert_one(contributor)
			pass
		
		
		self.redirect("/recommended/")


class ContributorsHandler(BaseHandler): #(tornado.web.RequestHandler):
	"""
	list all contributors from db.contributors
	"""
	def get(self):

		coll_contrib = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] #db.contributors
		contributors = list(coll_contrib.find())
		print "DataModelHandler.get / contributors :"
		pprint.pprint (contributors)

		# ### retrieve datamodel from DB
		# coll_dm = self.application.db[ MONGODB_COLL_DATAMODEL ]
		# data_model = list(coll_dm.find())
		# print "DataModelHandler.get / data_model :"
		# pprint.pprint (data_model)

		self.render(
			"contributors_list.html",
			page_title  	= app_main_texts["main_title"],
			header_text 	= "...",
			# data_model		= data_model,
			contributors 	= contributors
		)


class DataModelViewHandler(BaseHandler):
	"""
	list the fields of your data model from db.data_model
	"""
	def get(self) : 

		print "\nDataModelHandler.get... "

		### retrieve datamodel from DB
		coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]
		# data_model = list(coll_model.find())
		data_model_custom = list(coll_model.find({"field_class" : "custom"}))
		print "DataModelHandler.get / data_model_custom :"
		pprint.pprint (data_model_custom)

		data_model_core = list(coll_model.find({"field_class" : "core"}))
		print "DataModelHandler.get / data_model_core :"
		pprint.pprint (data_model_core)

		### test printing object ID
		print "DataModelHandler.get / data_model_core[0] object_ID :"
		print str(data_model_core[0]["_id"])

		self.render(
			"datamodel_view.html",
			page_title = app_main_texts["main_title"],
			datamodel_custom = data_model_custom,
			datamodel_core = data_model_core
		)
	


class DataModelEditHandler(BaseHandler):
	"""
	list the fields of your data model from db.data_model
	"""
	def get(self) : 
		print "\nDataModelHandler.get... "

		### retrieve datamodel from DB
		coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]
		# data_model = list(coll_model.find())
		data_model_custom = list(coll_model.find({"field_class" : "custom"}))
		print "DataModelHandler.get / data_model_custom :"
		pprint.pprint (data_model_custom)

		self.render(
			"datamodel_edit.html",
			page_title = app_main_texts["main_title"],
			datamodel_custom = data_model_custom,
		)

	def post(self):
		### get fields + objectIDs
		### 
		pass

class FormHandler(BaseHandler) : 
	"""
	test with basic Bulma Form
	"""
	def get(self):

		print "\FormHandler.get... "

		self.render(
			"form_instance.html",
			page_title = app_main_texts["main_title"],
		)

### TO DO 
class DataScrapedHandler(BaseHandler):
	"""
	list all data scraped from db.data_scraped 
	"""
	def get (self):
		pass


########################
### run spider handlers
"""
test_data_model = [
	

	# item source and
	"link_data", 
	"link_src", 
	"link_to",

	# item contents
	"title", 
	"img", 
	"abstract", 
	"tags", # keywords
	"raw_date", 

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

	### custom mandatory fields
	"name"  : "TEST", 
	# "label" : "test_spider_config",
	"page_url" : "http://quote.toscrape.com", # base url (ex : "https://www.mysite.org")
	"start_urls" : [ # List of URLs that will be crawled by the parse method
		'http://quotes.toscrape.com/'
	],

	### custom notes
	"notes" : u"test configuration for debugging / developping purposes...",

	### settings and logging fields
	"error_array" : [],
	"item_count": 0, # will be incremented each time a new item is created
	"item_count_depth_1" : 0,# will be incremented each time an item is completed in detailed page
	"LIMIT" : 10, # The number of pages where the spider will stop
	"page_count" : 1, # The number of pages already scraped
	"download_delay" : 0, # The delay in seconds between each request. some website will block too many requests


	### custom boolean on whether the page contains complete items or need to follow links
	"parse_follow" : False, 

	### custom info if website needs AJAX requests...
	"page_needs_splash" : False,

	### custom xpaths for next_page, filled by user
	"next_page_xpath" :'//li[@class="next"]/a/@href', 
	# "action_xpath" : "",  

	### custom xpaths for item, filled by user
	"abstract_xpath" : './span[@class="text"]/text()',
	"author_xpath" : './/small[@class="author"]/text()',
	"tags_xpath" : './/div[@class="tags"]/a[@class="tag"]/text()',
	"rawdate_xpath" : ""
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
"""

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
		spider_config = coll.find_one({"scraper_config.spidername": spidername})
		
		### redirect / set default runner if no spider_config
		if spider_config == None : 
			print "SpiderHandler.get --- !!! Spidername not found : test spider with test_config"
			# test_config = {
			# 		"name"  : "quote", 
			# 		"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],
			# 	 } 
			# (this will come from DB later)
			# spider_config = test_spider_config
			# self.redirect("/")			
			self.render(
				"index.html",
				page_title = app_main_texts["main_title"],
				header_text = "ERROR !!! there is no ''%s'' spider configuration in the DB ..." %(spidername),
				user = self.current_user
			)
		
		else : 
			print "SpiderHandler.get --- spidername : ", spidername
			print "SpiderHandler.get --- spider_config :"
			pprint.pprint(spider_config)

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

		print "SpiderHandler.run_spider --- creating data model list from fields in db "
		### getting data_model list (this will come from DB later)
		coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]
		data_model = coll_model.distinct("field_name")
		print "SpiderHandler.run_spider --- data_model from db :" 
		pprint.pprint(data_model)
		
		### for debugging
		# data_model = test_data_model 

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
			contributor=contributor,
		)
	
	def css_files(self):
		return "css/recommended.css"
	
	def javascript_files(self):
		return "js/recommended.js"