# -*- encoding: utf-8 -*-


import 	pprint 
from 	bson import ObjectId
import 	time
from 	functools import wraps

from pymongo import UpdateOne

import tornado.web, tornado.template
from tornado import gen

### import app settings / infos 
from config.app_infos import app_infos, app_main_texts
from config.settings_example import * # MONGODB_COLL_CONTRIBUTORS, MONGODB_COLL_DATAMODEL, MONGODB_COLL_DATASCRAPPED
from config.settings_corefields import *
from config.core_classes import SpiderConfig, UserClass

### import WTForms for validation
from forms import *

### import contributor generic class
from contributor import ContributorBaseClass

### OpenScraper generic scraper
from scraper import run_generic_spider 

### import item classes
from scraper import GenericItem




########################
########################
### DEFAULT / UTILS --- SOME STILL NOT TESTED

def create_generic_custom_fields():
	"""create default custom fields in DB """
	
	default_fields_list = []
	for default_field in DATAMODEL_DEFAULT_CUSTOM_FIELDS :
		new_field = {
			"field_name" 	: default_field["field_name"],
			"field_type" 	: default_field["field_type"],
			"added_by" 		: "admin",
			"field_class" 	: "custom",
		}
		default_fields_list.append(new_field)
	
	self.application.coll_model.insert_many(default_fields_list)

def reset_fields_to_default():
	"""reset datamodel to default : core fields and default custom fields"""

	self.application.coll_model.remove({})
	create_generic_custom_fields()

### DECORATORS / UTILS 
# cf : https://www.saltycrane.com/blog/2010/03/simple-python-decorator-examples/
# cf : https://www.codementor.io/sheena/advanced-use-python-decorators-class-function-du107nxsv
# cf : for requests : https://mrcoles.com/blog/3-decorator-examples-and-awesome-python/
# cf : https://stackoverflow.com/questions/6394511/python-functools-wraps-equivalent-for-classes

def print_separate(debug) :
	def print_sep(f):
		"""big up and self high-five ! it's the first real decorator I wrote my self, uuuh !!! """
		@wraps(f)
		def wrapped(*args, **kwargs):
			if debug == True :
				print "\n{}".format("---"*10)
			r = f(*args, **kwargs)
			return r
		return wrapped
	return print_sep



#### DECORATORS NOT WORKING FOR NOW

def time_this(original_function):
	print "decorating"
	def new_function(*args,**kwargs):
		print "starting decoration"
		x = original_function(*args,**kwargs)
		return x
	return new_function  

def time_all_class_methods(Cls):
	class NewCls(object):
		def __init__(self, *args, **kwargs):
			print args
			print kwargs
			self.oInstance = Cls(*args,**kwargs)
		def __getattribute__(self,s):
			"""
			this is called whenever any attribute of a NewCls object is accessed. This function first tries to 
			get the attribute off NewCls. If it fails then it tries to fetch the attribute from self.oInstance (an
			instance of the decorated class). If it manages to fetch the attribute from self.oInstance, and 
			the attribute is an instance method then `time_this` is applied.
			"""
			try:    
				x = super(NewCls,self).__getattribute__(s)
			except AttributeError:
				pass
			else:
				return x
			x = self.oInstance.__getattribute__(s)
			if type(x) == type(self.__init__): 	# it is an instance method
				return time_this(x)				# this is equivalent of just decorating the method with time_this
			else:
				return x
	return NewCls




########################
########################
### REQUEST HANDLERS ###
"""
Tornado supports any valid HTTP method (GET,POST,PUT,DELETE,HEAD,OPTIONS)
"""

########################
### BASE handler

class BaseHandler(tornado.web.RequestHandler):
	
	"""
	Base class for all routes : 
	all handler wil inheritate the following functions if writtent like this
	MyNewHandler(BaseHandler)
	"""

	### user functions for all pages
	def get_current_user(self):
		""" return user_name"""
		return self.get_secure_cookie("user_name")
	
	def get_current_user_email(self):
		""" return user_name"""
		return self.get_secure_cookie("user_email")

	def get_user_from_db(self, user_email) :
		""" get user from db"""
		user 	   = self.application.coll_users.find_one({"email": user_email })
		return user 

	def get_current_user_id(self):
		user_email = self.get_current_user_email()
		user 	   = self.application.coll_users.find_one({"email": user_email })
		return str(user["_id"])

	def add_user_to_db(self, user): 
		self.application.coll_users.insert_one( user )

	def set_current_user(self, user) :
		""" set cookie from user infos """
		if user : 
			# retrieve user data 
			user_name		= user["username"]
			user_password	= user["password"]
			user_email		= user["email"]

			self.set_secure_cookie("user_name", user_name )
			self.set_secure_cookie("user_email", user_email )
		else :
			self.clear_current_user()

	def clear_current_user(self):
		""" """
		# if (self.get_argument("logout", None)):
		self.clear_cookie("user_name")
		self.clear_cookie("user_email")

	### DB functions for all pages
	def get_datamodel_fields(self, query=None):
		"""return fields from query as list"""
		
		fields =[]

		if query=="custom":
			custom_fields = list(self.application.coll_model.find( { "field_class" : "custom" }))
			fields = [ str(f["_id"]) for f in custom_fields ]
			# equivalent to :
			# for custom_field in custom_fields :
			# 	custom_field_id = str(custom_field["_id"])
			# 	fields.append(custom_field_id)

		### get fields 
		if query in ["infos", "scraper_config"] : 
			pass

		return fields

	def count_documents(self, db_name="datamodel", query=None ) : 
		""" simple count of documents in the db collection db_name"""
		
		if db_name=="datamodel" :
			coll = self.application.coll_model
		if db_name=="contributors" :
			coll = self.application.coll_spiders
		if db_name=="data" :
			coll = self.application.coll_data
		if db_name=="users" :
			coll = self.application.coll_users

		count = coll.find(query).count()
		return count

	def count_all_documents(self):
		"""count all collections' documents in db"""
		collections_to_count = ["datamodel", "contributors", "data", "users" ]
		counts 	= { "count_{}".format(k) : self.count_documents(k) for k in collections_to_count }
		return counts


class PageNotFoundHandler(BaseHandler): 
	"""
	default handler to manage 404 errors
	"""
	def get(self):

		print "\nPageNotFoundHandler.post / request : "
		pprint.pprint (self.request )
		print "\nPageNotFoundHandler.post / request.arguments : "
		pprint.pprint( self.request.arguments )

		self.render("404.html",
					page_title  = app_main_texts["main_title"],
		)



######################################
### Login - logout - register handlers 
# cf : https://guillaumevincent.github.io/2013/02/12/Basic-authentication-on-Tornado-with-a-decorator.html
# cf : http://tornado-web.blogspot.fr/2014/05/tornado-user-authentication-example.html

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

				self.redirect("/")
			
			else : 
				self.redirect("/login")
		else : 
			self.redirect("/login")
	

class RegisterHandler(BaseHandler):
	""" register a user (check if exists in db first)  and set cookie"""

	def get(self):
	
		# print "\nRegisterHandler.post / request : "
		# pprint.pprint (self.request )
		# print "\nRegisterHandler.post / request.arguments : "
		# pprint.pprint( self.request.arguments )


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
		user = self.get_user_from_db( self.get_argument("email") )

		if user == None : 

			print "\nRegisterHandler.post / adding user to DB "
			
			user_dict = { 
				"username" 		: user_name,
				"email" 		: user_email,
				"password" 		: user_password,
				"level_admin" 	: "user",
				}
			user_object = UserClass(**user_dict) 
			print "\nRegisterHandler.post / user as UserClass instance "
			print user_object.__dict__

			self.add_user_to_db(user_dict)

			### set user
			self.set_current_user(user_dict)

			self.redirect("/")

		else : 
			### TO DO : add alert if user already exists
			self.redirect("/register")


class LogoutHandler(BaseHandler):
	def get(self):
		
		self.clear_current_user()
		self.redirect("/")


### TO DO 
class UserPreferences(BaseHandler):
	""" get/update user's infos, preferences, public key... """

	def get(self, user_id=None, token=None) : 
		self.redirect("/404")

	def post(self): 
		self.redirect("/404")


########################
### Index page 
class WelcomeHandler(BaseHandler):
	"""
	handler for index page
	"""
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	def get(self):
		
		print "\nWelcomeHandler.get... "

		### count collections' documents
		# count_dm 			= self.count_documents(db_name="datamodel", query={"field_class" : "custom"})
		# count_contributors 	= self.count_documents(db_name="contributors")
		# count_data 			= self.count_documents(db_name="data")
		# count_users 		= self.count_documents(db_name="users")
		counts = self.count_all_documents() 
		print "\nWelcomeHandler.get / counts :", counts

		self.render(
			"index.html",
			page_title  		= app_main_texts["main_title"],
			# count_dm 			= count_dm,
			# count_contributors 	= count_contributors,
			# count_data 			= count_data,
			# count_users 		= count_users,
			counts 				= counts,
			user				= self.current_user
		)

	# def write_error(self, status_code, **kwargs):
	# 	self.write("Gosh darnit, user! You caused a %d error." % status_code)


#####################################
### DATAMODEL lists / edit handlers

class DataModelViewHandler(BaseHandler):
	"""
	list the fields of your data model from db.data_model
	"""
	
	@print_separate(APP_DEBUG)
	def get(self) : 

		print "\nDataModelHandler.get... "

		### retrieve datamodel from DB
		data_model_custom = list(self.application.coll_model.find({"field_class" : "custom"}).sort("field_name",1) )
		print "DataModelHandler.get / data_model_custom :"
		pprint.pprint (data_model_custom)

		data_model_core = list(self.application.coll_model.find({"field_class" : "core"}).sort("field_name",1) )
		print "DataModelHandler.get / data_model_core :"
		pprint.pprint (data_model_core)

		### test printing object ID
		print "DataModelHandler.get / data_model_core[0] object_ID :"
		print str(data_model_core[0]["_id"])

		self.render(
			"datamodel_view.html",
			page_title 			= app_main_texts["main_title"],
			datamodel_custom 	= data_model_custom,
			datamodel_core 		= data_model_core,

		)


class DataModelEditHandler(BaseHandler):
	"""
	list the fields of your data model from db.data_model
	"""
	@print_separate(APP_DEBUG)
	def get(self) : 
		print "\nDataModelHandler.get... "

		### retrieve datamodel from DB
		data_model_custom = list(self.application.coll_model.find({"field_class" : "custom"}))
		print "DataModelHandler.get / data_model_custom :"
		pprint.pprint (data_model_custom)

		self.render(
			"datamodel_edit.html",
			page_title 	= app_main_texts["main_title"],
			field_types = DATAMODEL_FIELDS_TYPES,
			datamodel_custom = data_model_custom,
		)

	@print_separate(APP_DEBUG)
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

		# first : update fields in DB
		print "DataModelEditHandler.post / updating fields :  "
		operations =[ UpdateOne( 
			{"_id" : field["_id"]},
			{'$set':  { 
					"field_type" 	: field["field_type"],
					"field_name" 	: field["field_name"],
					"modified_by"	: self.get_current_user_email()	
					 } 
			}, 
			upsert=True ) for field in updated_fields 
		]
		self.application.coll_model.bulk_write(operations)

		# then : delete fields in db 
		print "DataModelEditHandler.post / deleting fields :  "
		for field in updated_fields :
			if field["field_keep"] == "delete" :
				# field_in_db = self.application.coll_model.find_one({"_id" : field["_id"]})
				# print field_in_db
				self.application.coll_model.delete_one({"_id" : field["_id"]})
				# coll_model.remove({"_id" : field["_id"]})

		### redirect once finished
		self.redirect("/datamodel/view")


class DataModelAddFieldHandler(BaseHandler) : 
	"""
	Add a new field to your data model 
	"""
	@print_separate(APP_DEBUG)
	def get(self) : 

		print "\nDataModelAddFieldHandler.get... "

		self.render(
			"datamodel_new_field.html",
			page_title = app_main_texts["main_title"],
			field_types = DATAMODEL_FIELDS_TYPES
		)

	@print_separate(APP_DEBUG)
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
			"added_by" 		: self.get_current_user_email(),
			"field_class" 	: "custom",
		}
		print "DataModelAddFieldHandler.post / new_field : ", new_field

		### insert new field to db
		self.application.coll_model.insert_one(new_field)


		self.redirect("/datamodel/edit")



#####################################
### CONTRIBUTOR lists / edit handlers

class ContributorsHandler(BaseHandler): #(tornado.web.RequestHandler):
	"""
	list all contributors from db.contributors
	"""
	@print_separate(APP_DEBUG)
	def get(self):

		print "\nContributorsHandler.get ..."

		contributors = list(self.application.coll_spiders.find())
		print "\nContributorsHandler.get / contributors :"
		pprint.pprint (contributors[0])
		print '.....\n'

		self.render(
			"contributors_list.html",
			page_title  	= app_main_texts["main_title"],
			contributors 	= contributors
		)


class ContributorEditHandler(BaseHandler): #(tornado.web.RequestHandler):
	"""
	contributor edit handler
	"""

	@print_separate(APP_DEBUG)
	def get(self, spider_id=None):
		"""show infos on one contributor : get info in DB and prefill form"""
		
		print "\nContributorEditHandler.get / spider_id : ", spider_id

		### retrieve datamodel - custom fields
		data_model = list(self.application.coll_model.find( {"field_class" : "custom"})) #, {"field_name":1, "_id":1} ))
		data_model = [ { k : str(v) for k,v in i.iteritems() } for i in data_model ]
		# print "\nContributorEditHandler.get / data_model : "
		# pprint.pprint(data_model)

		contributor_edit_fields = CONTRIBUTOR_EDIT_FIELDS
		# print "\nContributorEditHandler.get / contributor_edit_fields :"
		# pprint.pprint(contributor_edit_fields)

		### retrieve contributor data from spidername

		# spider exists ( edit form ) 
		if spider_id :
			try : 
				create_or_update	= "update"
				contributor			= self.application.coll_spiders.find_one({"_id": ObjectId(spider_id)})
			except :
				self.redirect("/404")

		# spider doesn't exist : add form
		else :
			# core empty contributor structure to begin with
			contributor_object 	= SpiderConfig()
			contributor 		= contributor_object.full_config_as_dict()
			create_or_update	= "create"

		print "\nContributorEditHandler.get / contributor :"
		pprint.pprint(contributor)

		### render page
		self.render("contributor_edit.html",
			page_title 				= app_main_texts["main_title"],
			create_or_update 		= create_or_update,
			contributor_edit_fields = contributor_edit_fields,
			contributor 			= contributor,
			datamodel				= data_model,
		)


	@print_separate(APP_DEBUG)
	def post(self, spider_id=None):
		"""update or create new contributor spider in DB"""

		print "\nContributorEditHandler.post... spider_id : ", spider_id
		
		### TO DO : form validation
		
		### get form back from client
		spider_config_form = self.request.arguments
		print "\nContributorEditHandler.post / spider_config_form : "
		pprint.pprint( spider_config_form )

		is_new = True
		# check if spider already exists
		if spider_id != None : 
			spider_id = spider_config_form["_id"][0]
			is_new = False

		# check if website is already crawled by another spider
		similar_spider = self.application.coll_spiders.find( {"infos.page_url": spider_config_form["page_url"]} )
		if similar_spider and is_new :
			print "\nContributorEditHandler.post / already a similar spider ... "
			self.redirect("/contributors")

		# populate a contributor object
		print "\nContributorEditHandler.post / creating spider with SpiderConfig class  ... "
		contributor_object = SpiderConfig( 
				form 		= spider_config_form,
				new_spider 	= is_new,
				user		= self.get_current_user_email() 
		)

		### get spider identifier from form
		pprint.pprint(spider_config_form)

		if spider_id and spider_id != "new_spider":
			
			print "\nContributorEditHandler.post / spidername already exists : "

			# getting id from form
			spider_oid = ObjectId(spider_id)

			# getting back spider config from db but from its _id
			contributor = self.application.coll_spiders.find_one( {"_id": ObjectId(spider_oid)} )
			new_config 	= contributor_object.partial_config_as_dict( previous_config = contributor )

			# update contributor
			old_fields = {"infos" :1 , "scraper_config" : 1 , "scraper_config_xpaths" : 1 }
			self.application.coll_spiders.update_one( {"_id": spider_oid}, { "$unset": old_fields } )
			self.application.coll_spiders.update_one( {"_id": spider_oid}, { "$set": new_config  } , upsert=True )

		else :
			contributor = contributor_object.full_config_as_dict()
			# insert new spider to db
			self.application.coll_spiders.insert_one(contributor)

		print "\nContributorEditHandler.post / contributor :"
		pprint.pprint(contributor)

		### redirections for debugging purposes
		# if spider_id and spider_id!= "new_spider" :
		# 	self.redirect("/contributor/edit/{}".format(spider_id))
		# else : 
		# 	self.redirect("/contributor/add")
		
		### real redirection
		self.redirect("/contributors")


### TO DO 
class ContributorDeleteHandler(BaseHandler) : 
	"""
	delete a spider config
	"""
	def get(self, spidername=None):
		print "\nContributorDeleteHandler.get / contributors :"
		self.redirect("/404")

	def post(self):
		print "\nContributorDeleteHandler.get / contributors :"
		self.redirect("/404")


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
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@gen.coroutine
	def get(self, spider_id = None ):
		
		print "\nSpiderHandler.get... "
		counts = self.count_all_documents() 

		### retrieve spider config from its name in the db
		# spider_config = self.application.coll_spiders.find_one({"scraper_config.spidername": spidername})
		spider_config = self.application.coll_spiders.find_one({"_id": ObjectId(spider_id) })
		
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
				page_title 	= app_main_texts["main_title"],
				serv_msg 	= "ERROR !!! there is no ''%s'' spider configuration in the DB ..." %(spider_id),
				user 		= self.current_user,
				counts 		= counts
			)
		
		else : 
			print "SpiderHandler.get --- spider_id : ", spider_id
			print "SpiderHandler.get --- spider_config :"
			pprint.pprint(spider_config)

			print "SpiderHandler.get --- starting spider runner --- "
			### TO DO : CHECK IF REALLY WORKING : asynchronous run the corresponding spider
			# run_generic_spider( run_spider_config = spider_config ) # synchronous
			yield self.run_spider( spider_id, spider_config=spider_config ) # asynchronous

			### update scraper_log.is_working
			self.application.coll_spiders.update_one( {"_id": ObjectId(spider_id) }, {"$set" : {"scraper_log.is_working" : True}})

			### TO DO : redirect to a page showing crawling status / results
			# self.redirect("/contributors/")
			self.render(
				"index.html",
				page_title 	= app_main_texts["main_title"],
				serv_msg 	= "crawling of -%s- launched ..." %(spider_id),
				user 		= self.current_user,
				counts 		= counts
			)

	@print_separate(APP_DEBUG)
	@gen.coroutine
	def run_spider (self, spider_id, spider_config) :
		
		print "\nSpiderHandler.run_spider --- "

		### getting data_model lists
		print "SpiderHandler.run_spider --- creating data model list from fields in db "
		# data_model 			= self.application.coll_model.distinct("field_name")
		data_model 			= list(self.application.coll_model.find({}))
		# data_model_custom 	= list(self.application.coll_model.find({"field_type" : "custom" }))
		# data_model_core 	= list(self.application.coll_model.find({"field_type" : "core" }))
		
		# print "SpiderHandler.run_spider --- data_model from db :" 
		# pprint.pprint(data_model)
		
		### for debugging
		# data_model = test_data_model 

		### run spider --- check masterspider.py --> function run_generic_spider()
		result = run_generic_spider( 
									spider_id			= spider_id, 
									datamodel			= data_model, 
									run_spider_config	= spider_config 
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

		form = SampleForm()

		if form.validate():
			# do something with form.username or form.email
			pass

		self.render(
			"form_instance.html",
			page_title = app_main_texts["main_title"],
			form = form
		)

		# self.write(templates.load("simpleform.html").generate(
		# 		compiled=compiled, 
		# 		page_title = app_main_texts["main_title"],
		# 		form=form))

	def post(self):
		
		print "\FormHandler.post... "

		### get form back from client
		form = SampleForm(self.request.arguments)
		print "\nFormHandler.post / spider_config_form : "
		pprint.pprint( form )


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