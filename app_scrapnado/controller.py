import pprint 
from bson import ObjectId

from pymongo import UpdateOne

import tornado.web, tornado.template
from tornado import gen

### import app settings / infos 
from config.app_infos import app_infos, app_main_texts
from config.settings_example import * # MONGODB_COLL_CONTRIBUTORS, MONGODB_COLL_DATAMODEL, MONGODB_COLL_DATASCRAPPED
from config.settings_corefields import *

# ### import WTForms for validation
# from wtforms import validators 
# from tornadotools.forms import Form
from forms import *

### import contributor generic class
from contributor import ContributorBaseClass

### OpenScraper generic scraper
from scraper import run_generic_spider 

### import item classes
from scraper import GenericItem




########################
########################
### DEFAULT / UTILS --- NOT TESTED

def create_generic_custom_fields():
	"""create default custom fields in DB """
	
	coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]

	default_fields_list = []
	for default_field in DATAMODEL_DEFAULT_CUSTOM_FIELDS :
		new_field = {
			"field_name" 	: default_field["field_name"],
			"field_type" 	: default_field["field_type"],
			"added_by" 		: "admin",
			"field_class" 	: "custom",
		}
		default_fields_list.append(new_field)
	
	coll_model.insert_many(default_fields_list)

def reset_fields_to_default():
	"""reset datamodel to default : core fields and default custom fields"""
	coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]
	coll_model.remove({})
	create_generic_custom_fields()


########################
########################
### REQUEST HANDLERS ###
"""
Tornado supports any valid HTTP method (GET,POST,PUT,DELETE,HEAD,OPTIONS)
"""

########################
### BASE handler

class BaseHandler(tornado.web.RequestHandler):
	
	def get_current_user(self):
		""" return user_name"""
		return self.get_secure_cookie("user_name")
	
	def get_current_user_email(self):
		""" return user_name"""
		return self.get_secure_cookie("user_email")

	def get_user_from_db(self, user_email) :
		""" get user from db"""
		coll_users = self.application.db[ MONGODB_COLL_USERS ]
		# user 	   = coll_users.find_one({"email": self.get_argument("email") })
		user 	   = coll_users.find_one({"email": user_email })
		return user 

	def add_user_to_db(self, user): 

		coll_users = self.application.db[ MONGODB_COLL_USERS ]
		coll_users.insert_one( user )

	def set_current_user(self, user) :
		""" set cookie from user infos """
		if user : 
			# retrieve user data 
			user_name		= user["username"]
			user_password	= user["password"]
			user_email		= user["email"]

			self.set_secure_cookie("user_name", user_name )
			self.set_secure_cookie("user_email", user_email )
		else:
			self.clear_current_user()

	def clear_current_user(self):
		# if (self.get_argument("logout", None)):
		self.clear_cookie("user_name")
		self.clear_cookie("user_email")


class PageNotFoundHandler(BaseHandler): 
	def get(self):
		self.render("404.html",
					page_title  = app_main_texts["main_title"],
		)



######################################
### Login - logout - register handlers 

class LoginHandler(BaseHandler):
	
	def get(self):

		print "\nLoginHandler.get ... "

		### TO DO : add WTForms as form 

		self.render('login.html',
			page_title  = app_main_texts["main_title"],
			login_or_register = "login"
		)
	
	def post(self):
		""" check if user exists in db and set cookie"""
		self.check_xsrf_cookie()

		print "\nLoginHandler.post ... "

		print "\nLoginHandler.post / request.arguments ... "
		# print self.request 
		print self.request.arguments 

		### get user from db
		# coll_users = self.application.db[ MONGODB_COLL_USERS ]
		# user 	   = coll_users.find_one({"email": self.get_argument("email") })
		user = self.get_user_from_db( self.get_argument("email") )
		print "LoginHandler.post / user :"
		print user

		### TO DO : form validation 

		### check if user exists in db
		if user : 

			user_password	= user["password"]
			# check password 
			if self.get_argument("password") == user_password : 
				
				# set user
				self.set_current_user(user)

				# # retrieve user data 
				# user_name		= user["username"]
				# user_password	= user["password"]
				# user_email		= user["email"]


				# if self.get_argument("password") == user_password : 
				# 	self.set_secure_cookie("user_name", user_name )
				# 	self.set_secure_cookie("user_email", user_email )

				self.redirect("/")
			
			else : 
				self.redirect("/login")
		else : 
			self.redirect("/login")
	

class RegisterHandler(BaseHandler):
	""" register a user (check if exists in db first)  and set cookie"""

	def get(self):
	
		print "\nRegisterHandler.get ... "

		self.render('login.html',
			page_title  = app_main_texts["main_title"],
			login_or_register = "register"
		)

	def post(self):
		""" check if user exists in db, insert it in db, and set cookie"""
		
		self.check_xsrf_cookie()
		print "\nRegisterHandler.post ... "

		### get user infos + data validation
		user_name 		= self.get_argument("username")
		user_email 		= self.get_argument("email")
		user_password 	= self.get_argument("password")

		### TO DO : form validation
		print "RegisterHandler.post / request.arguments ... "
		# print self.request 
		print self.request.arguments 

		### get user from db
		# coll_users = self.application.db[ MONGODB_COLL_USERS ]
		# user 	   = coll_users.find_one({"email": self.get_argument("email") })
		user = self.get_user_from_db( self.get_argument("email") )

		if user == None : 

			print "\RegisterHandler.post / adding user to DB "
			
			user_dict = { 
				"username" 	: user_name,
				"email" 	: user_email,
				"password" 	: user_password,
				"level_admin" : "user",
				}
			self.add_user_to_db(user_dict)
			# coll_users.insert_one( user_dict )

			### set user
			# self.set_secure_cookie("user_name", user_name )
			# self.set_secure_cookie("user_email", user_email )
			self.set_current_user(user_dict)

			self.redirect("/")

		else : 
			self.redirect("/register")


class LogoutHandler(BaseHandler):
	def get(self):
		
		self.clear_current_user()
		self.redirect("/")


########################
### Index page 
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
			# header_text = app_main_texts["main_header"],
			user=self.current_user
		)

	# def write_error(self, status_code, **kwargs):
	# 	self.write("Gosh darnit, user! You caused a %d error." % status_code)


#####################################
### DATA MODEL lists / edit handlers

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
			page_title 	= app_main_texts["main_title"],
			field_types = DATAMODEL_FIELDS_TYPES,
			datamodel_custom = data_model_custom,
		)

	def post(self):

		### get fields + objectIDs
		print "\nDataModelEditHandler.post ..."

		raw_updated_fields = self.request.arguments

		### TO DO : form validation

		# print "DataModelEditHandler.post / raw_updated_fields : "
		# # print self.request 
		# pprint.pprint( raw_updated_fields )

		post_keys = self.request.arguments.keys()
		print "DataModelEditHandler.post / post_keys :  "
		post_keys.remove("_xsrf")
		print post_keys

		# clean post args from _xsrf
		del raw_updated_fields['_xsrf']
		print "DataModelEditHandler.post / raw_updated_fields :  "
		pprint.pprint( raw_updated_fields )
		# print( type(raw_updated_fields) )

		# recreate fields 
		updated_fields = []
		for i, field_id in  enumerate(raw_updated_fields["_id"]):
			field = { 
				k : raw_updated_fields[k][i] for k in post_keys
			}
			updated_fields.append(field)
		# _id back to object id
		for field in updated_fields : 
			field["_id"] = ObjectId(field["_id"])
		print "DataModelEditHandler.post / updated_fields :  "
		pprint.pprint(updated_fields)


		### DELETE / UPDATE FIELDS
		coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]


		# first : update fields in DB
		print "DataModelEditHandler.post / updating fields :  "
		operations =[ UpdateOne( 
			{"_id" : field["_id"]},
			{'$set':  { 
					"field_type" 	: field["field_type"],
					"field_name" 	: field["field_name"],
					 } 
			}, 
			upsert=True ) for field in updated_fields 
		]
		coll_model.bulk_write(operations)

		# then : delete fields in db 
		print "DataModelEditHandler.post / deleting fields :  "
		for field in updated_fields :
			if field["field_keep"] == "delete" :
				field_in_db = coll_model.find_one({"_id" : field["_id"]})
				print field_in_db
				coll_model.delete_one({"_id" : field["_id"]})
				# coll_model.remove({"_id" : field["_id"]})

		### redirect once finished
		self.redirect("/datamodel/edit")


class DataModelAddFieldHandler(BaseHandler) : 
	"""
	Add a new field to your data model 
	"""
	def get(self) : 

		print "\nDataModelAddFieldHandler.get... "

		self.render(
			"datamodel_new_field.html",
			page_title = app_main_texts["main_title"],
			field_types = DATAMODEL_FIELDS_TYPES
		)

	def post(self):

		print "\nDataModelAddFieldHandler.post ..."
		
		### TO DO : form validation
		print "DataModelAddFieldHandler.post / request.arguments ... "
		# print self.request 
		pprint.pprint( self.request.arguments )

		### add field to datamodel 
		
		# add complementary infos to create a full field
		new_field = {
			"field_name" 	: self.get_argument("field_name"),
			"field_type" 	: self.get_argument("field_type"),
			"added_by" 		: self.get_current_user(),
			"field_class" 	: "custom",
		}
		print "DataModelAddFieldHandler.post / new_field : ", new_field

		### insert new field to db
		coll_model = self.application.db[ MONGODB_COLL_DATAMODEL ]
		coll_model.insert_one(new_field)


		self.redirect("/datamodel/edit")



#####################################
### CONTRIBUTOR lists / edit handlers

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

		# data_model_next_page = coll_model.find_one( {"field_name" : "next_page"}) #, {"field_name":1, "_id":1} )
		# data_model_next_page = { k : str(v) for k,v in data_model_next_page.iteritems() }
		# print "\n... ContributorEditHandler.get / data_model_next_page : "
		# pprint.pprint(data_model_next_page)

		contributor_edit_fields = CONTRIBUTOR_EDIT_FIELDS
		print "\n... ContributorEditHandler.get / contributor_edit_fields :"
		pprint.pprint(contributor_edit_fields)


		### retrieve contributor data from spidername
		# core empty contributor structure to begin with
		contributor = CONTRIBUTOR_CORE_FIELDS
		# spider exists : edit form
		if spidername:
			coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] 
			contributor = coll.find_one({"scraper_config.spidername": spidername})
		# new spider : add form
		else :
			pass 
		print "\n... ContributorEditHandler.get / contributor :"
		pprint.pprint(contributor)

		### render page
		self.render("contributor_edit.html",
			page_title 	= app_main_texts["main_title"],
			# header_text = "Edit contributor",
			contributor_edit_fields = contributor_edit_fields,
			contributor = contributor,
			datamodel	= data_model,
			# datamodel_next_page	= data_model_next_page,
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
			# header_text 	= "...",
			# data_model		= data_model,
			contributors 	= contributors
		)




#####################################
### DATA lists / edit handlers

### TO DO - after item pipeline

class DataScrapedHandler(BaseHandler):
	"""
	list all data scraped from db.data_scraped 
	"""
	def get (self):
		self.redirect("/404")

class DataScrapedViewOneHandler(BaseHandler):
	"""
	list all data scraped from db.data_scraped 
	"""
	def get (self, spidername=None):
		self.redirect("/404")


########################
### RUN SPIDER handlers
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



#####################################
### SNIPPETS handlers

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