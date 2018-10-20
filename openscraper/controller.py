# -*- encoding: utf-8 -*-

from 	tornado.log import enable_pretty_logging, LogFormatter, access_log, app_log, gen_log

gen_log.info("--> importing .controller")


# import base handler and some utils..;
# controller being downhill from base_handler means that 
# doing so imports also many basic libs : pprint, math, 
from 	base_utils import *
from 	base_handler import *

# import 	pprint 
# from 	bson import ObjectId
# import 	time
# import 	math
# from 	datetime import datetime
# from 	functools import wraps
# import	urllib
# from 	copy import deepcopy

# import pymongo utils for bulk jobs
from 	pymongo import UpdateOne

# import 	tornado.web, tornado.template, tornado.escape

# import toro # deprecated it seems
# from 	tornado.ioloop import IOLoop
# from 	tornado import gen, concurrent
# from 	tornado.concurrent import return_future, run_on_executor
# from 	tornado.log import access_log, app_log, gen_log # already imported from base_handler

# from 	concurrent.futures import ThreadPoolExecutor # note : need to install "futures" in pytohn 2.7 : pip install futures
# from 	spider_threading import *
# from 	handler_threading import *


### import app settings / infos 
# from config.app_infos 			import app_infos, app_main_texts
# from config.settings_example 	import * # MONGODB_COLL_CONTRIBUTORS, MONGODB_COLL_DATAMODEL, MONGODB_COLL_DATASCRAPPED
# from config.settings_corefields import * # USER_CORE_FIELDS, etc...
# from config.settings_queries 	import * # QUERY_DATA_BY_DEFAULT, etc...
# from config.core_classes		import * # SpiderConfig, UserClass, QuerySlug
# from config.settings_threading	import * # THREADPOOL_MAX_WORKERS, etc...


### TO IMPROVE

### import WTForms for validation
from forms import *





############################################################################################
##################################    REQUEST HANDLERS    ##################################
############################################################################################
"""
Notes :
- Tornado supports any valid HTTP method (GET,POST,PUT,DELETE,HEAD,OPTIONS)
- BaseHandler loaded from base_handler.py
"""



### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### ERROR HANDLERS ##########################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class PageNotFoundHandler(BaseHandler): 
	"""
	default handler to manage 404 errors
	"""

	@print_separate(APP_DEBUG)
	@check_user_permissions
	def get(self):

		self.site_section 	= "404"
		# self.error_msg		= "404 - page not found"

		print 
		app_log.info("PageNotFoundHandler.post / uri : %s ", pformat(self.request.uri ) )
		# pprint.pprint (self.request.uri )

		app_log.info("PageNotFoundHandler.post / self.is_user_connected : %s ", pformat(self.is_user_connected ) )
		# print self.is_user_connected

		app_log.warning("PageNotFoundHandler.post / request : \n %s ", pformat(self.request ) )
		# pprint.pprint (self.request )
		
		app_log.info("PageNotFoundHandler.post / request.arguments : \n %s ", pformat(self.request.arguments ) )
		# pprint.pprint( self.request.arguments )

		self.set_status(404)
		self.render("404.html",

			page_title  		= app_main_texts["main_title"],
			
			site_section 		= self.site_section,
			
			error_msg 			= self.error_msg,
			
			user				= self.current_user,
			is_user_connected 	= self.is_user_connected,
			user_email			= self.user_email,
			user_auth_level		= self.user_auth_level,
			user_auth_level_dict = self.user_auth_level_dict
		)



### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### INDEX PAGE ##############################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class WelcomeHandler(BaseHandler):
	"""
	handler for index page
	"""

	@print_separate(APP_DEBUG)
	# @tornado.web.authenticated
	@check_user_permissions
	def get(self):
		
		app_log.info("WelcomeHandler.get... \n")

		self.site_section = "index"

		# catch error message if any
		self.catch_error_message()

		### count collections' documents
		counts = self.count_all_documents( 
					q_datamodel		= {"field_class" : "custom"},		 # query : just count custom fields
					q_contributors	= {"scraper_log.is_working" : True } # query : just count working and tested spiders
					) 
		app_log.info("WelcomeHandler.get / counts : \n  %s" , pformat(counts) )

		self.render( "index.html",

			page_title  		= app_main_texts["main_title"],
			site_section 		= self.site_section,
			counts 				= counts,
			
			user				= self.current_user,
			is_user_connected 	= self.is_user_connected,
			user_email			= self.user_email,
			user_auth_level		= self.user_auth_level,
			user_auth_level_dict = self.user_auth_level_dict,

			error_msg			= self.error_msg,
		)

	# def write_error(self, status_code, **kwargs):
	# 	self.write("Gosh darnit, user! You caused a %d error." % status_code)



### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### LOGIN - LOGOUT - REGISTER HANDLERS ######################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

# cf : https://guillaumevincent.github.io/2013/02/12/Basic-authentication-on-Tornado-with-a-decorator.html
# cf : http://tornado-web.blogspot.fr/2014/05/tornado-user-authentication-example.html

class LoginHandler(BaseHandler):
	
	@print_separate(APP_DEBUG)
	def get(self):
		
		print 
		app_log.info("LoginHandler.get ... ")

		self.site_section 	= "login"

		# catch error message if any
		self.catch_error_message()

		app_log.info("LoginHandler.get / next : ")
		next_url = self.get_argument('next', '/')
		app_log.info(next_url)

		# catch error if any
		self.catch_error_message()

		### TO DO : add WTForms as form 

		self.render('login_register.html',
			page_title  		= app_main_texts["main_title"],
			site_section		= self.site_section,
			login_or_register 	= "login",
			next_url			= next_url,
			error_msg			= self.error_msg,
			is_user_connected 	= self.is_user_connected
		)
	
	@print_separate(APP_DEBUG)
	def post(self):
		""" check if user exists in db and set cookie"""
		
		# self.check_xsrf_cookie()

		print 
		app_log.info("LoginHandler.post ...\n")
		
		app_log.info("LoginHandler.post / next_url : ")
		
		next_url = self.get_argument('next', '/')
		
		app_log.info( "%s - %s", next_url, type(next_url) )

		app_log.info("LoginHandler.post / request.arguments ... ")
		app_log.info( self.request.arguments )

		### get user from db
		user = self.get_user_from_db( self.get_argument("email") )
		app_log.info("LoginHandler.post / user : %s", user)
		# app_log.info( user )

		### TO DO : form validation 
		# form validation here....


		### check if user exists in db
		if user : 

			user_password	= user["password"]
			
			# check password 
			# TO DO : hash and/or decrypt password
			if self.get_argument("password") == user_password : 
				
				# set user
				self.set_current_user(user)

				# self.redirect("/")
				self.redirect( next_url )
			
			else : 
				# add error message and redirect if user wrote wrong password
				self.error_slug = self.add_error_message_to_slug("bad password or email mate ! no id stealing around here... mate !")
				self.redirect("/login/" + self.error_slug )
		
		else : 
			# add error message and redirect if no user registred in db
			# error_slug 		= u"?error=" + tornado.escape.url_escape("Login incorrect")
			self.error_slug = self.add_error_message_to_slug("incorrect login mate ! try again ")
			self.redirect("/login/" + self.error_slug)
	

class RegisterHandler(BaseHandler):
	""" register a user (check if exists in db first)  and set cookie"""

	@print_separate(APP_DEBUG)
	def get(self):
		
		print
		app_log.info("RegisterHandler.get ... ")

		self.site_section = "register"

		# print "\nRegisterHandler.post / request : "
		# pprint.pprint (self.request )
		# print "\nRegisterHandler.post / request.arguments : "
		# pprint.pprint( self.request.arguments )

		# catch error message if any
		self.catch_error_message()

		next_url = self.get_argument('next', u'/')
		app_log.info("RegisterHandler.get / next_url : %s", next_url ) 
		# print next_url

		self.render('login_register.html',
			page_title  		= app_main_texts["main_title"],
			site_section		= self.site_section,
			next_url 			= next_url,
			login_or_register 	= "register",
			error_msg			= self.error_msg,
			is_user_connected 	= self.is_user_connected

		)

	@print_separate(APP_DEBUG)
	def post(self):
		""" check if user exists in db, insert it in db, and set cookie"""

		# self.check_xsrf_cookie()
		print
		app_log.info("RegisterHandler.post ... ")

		next_url = self.get_argument('next', u'/')
		app_log.info("RegisterHandler.post / next_url : %s ", next_url)
		# print next_url

		timestamp = time.time()

		### get user infos + data validation
		user_name 		= self.get_argument("username")
		user_email 		= self.get_argument("email")
		user_password 	= self.get_argument("password")

		### TO DO : form validation
		# basic validation
		if user_name != "" and user_email != "" and user_password != "" :		
		
			app_log.info("RegisterHandler.post / request.arguments : %s", self.request.arguments )
			# print self.request 
			# print self.request.arguments 

			### get user from db
			user = self.get_user_from_db( self.get_argument("email") )

			if user == None : 

				app_log.info("RegisterHandler.post / adding user to DB ")
				
				user_level = "user"
				# add first user of the app as admin if no user are registred at all 
				users_registred = self.application.coll_users.find({})
				if users_registred.count() == 0 :
					app_log.warning("RegisterHandler.post / adding FIRST user to DB ")
					user_level = "admin"

				user_dict = { 
					"username" 		: user_name,
					"email" 		: user_email,
					"password" 		: user_password,
					"level_admin" 	: user_level,
					"added_at"		: timestamp
					}
				user_object = UserClass(**user_dict) 
				app_log.info("RegisterHandler.post / user as UserClass instance : %s", pformat(user_object.__dict__))
				# print user_object.__dict__

				self.add_user_to_db(user_dict)

				### set user
				self.set_current_user(user_dict)

				# self.redirect("/")
				self.redirect( next_url )

			else : 
				### add alert and redirect if user already exists
				self.error_slug = self.add_error_message_to_slug("user email already exists... mate !")
				self.redirect("/register/" + self.error_slug )
			
		else : 
			### add alert and redirect if user didn't fill some fields
			self.error_slug = self.add_error_message_to_slug("put your glasses mate ! you missed fields in form !")
			self.redirect("/register/" + self.error_slug )


class LogoutHandler(BaseHandler):

	@print_separate(APP_DEBUG)
	def get(self):
		"""simple logout function to clear cookies"""

		self.clear_current_user()
		self.redirect("/")


### TO DO : add form to show and edit user preferences
class UserPreferences(BaseHandler):
	""" get/update user's infos, preferences, public key... """

	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def get(self, user_id=None, token=None) : 
		self.redirect("/404")

	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def post(self): 
		self.redirect("/404")




### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### DATAMODEL lists / edit handlers #########################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class DataModelViewHandler(BaseHandler):
	"""
	list the fields of your data model from db.data_model
	"""
	
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated		
	@check_user_permissions
	def get(self) : 

		print
		app_log.info("DataModelViewHandler.get... ")

		self.site_section = "datamodel"

		# catch error message if any
		self.catch_error_message()





		### retrieve datamodel from DB
		data_model_custom = list(self.application.coll_model.find({"field_class" : "custom"}).sort("field_name",1) )
		app_log.info("DataModelViewHandler.get / data_model_custom[0:2] : \n %s \n ...", pformat(data_model_custom[0:2]) )

		data_model_core = list(self.application.coll_model.find({"field_class" : "core"}).sort("field_name",1) )
		app_log.info("DataModelViewHandler.get / data_model_core[0:2] : \n %s \n ... ", pformat(data_model_core[0:2]) )





		### test printing object ID
		app_log.info("DataModelViewHandler.get / data_model_core[0] object_ID : %s ", str( data_model_core[0]["_id"]) )

		self.render(
			"datamodel_view.html",
			page_title 			= app_main_texts["main_title"],
			site_section		= self.site_section,
			
			datamodel_custom 	= data_model_custom,
			datamodel_core 		= data_model_core,
			error_msg			= self.error_msg,
			
			user				= self.current_user,
			is_user_connected 	= self.is_user_connected,
			user_email			= self.user_email,
			user_auth_level		= self.user_auth_level,
			user_auth_level_dict = self.user_auth_level_dict,
		)


class DataModelEditHandler(BaseHandler):
	"""
	list the fields of your data model from db.data_model
	"""
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def get(self) : 
		
		print 
		app_log.info("DataModelEditHandler.get... " )

		self.site_section = "datamodel"

		# catch error message if any
		self.catch_error_message()


		# redirect if user doesn't have adapted auth level
		auth_level = self.user_auth_level_dict[self.site_section]
		self.redirect_user_if_not_authorized(auth_level, self.site_section)


		### retrieve datamodel from DB
		data_model_custom = list(self.application.coll_model.find({"field_class" : "custom"}))
		app_log.info("DataModelEditHandler.get / data_model_custom[0:2] : \n %s \n ...", pformat(data_model_custom[0:2])  )
		# pprint.pprint (data_model_custom)

		self.render(
			"datamodel_edit.html",
			page_title 			= app_main_texts["main_title"],
			site_section		= self.site_section,
			
			field_types 		= DATAMODEL_FIELDS_TYPES,
			field_keep_vars	 	= DATAMODEL_FIELD_KEEP_VARS,
			field_open_vars	 	= DATAMODEL_FIELD_OPEN_VARS,
			
			datamodel_custom 	= data_model_custom,
			error_msg			= self.error_msg,
			
			user				= self.current_user,
			is_user_connected 	= self.is_user_connected,
			user_email			= self.user_email,
			user_auth_level		= self.user_auth_level,		
			user_auth_level_dict = self.user_auth_level_dict,
			) 

	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def post(self):

		### get fields + objectIDs
		print
		app_log.info("DataModelEditHandler.post ..." )

		raw_updated_fields 	= self.request.arguments
		timestamp			= time.time()
		
		### TO DO : form validation

		# print "DataModelEditHandler.post / raw_updated_fields : "
		# # print self.request 
		# pprint.pprint( raw_updated_fields )

		### READ POST FORM

		post_keys = self.request.arguments.keys()
		post_keys.remove("_xsrf")
		app_log.info("DataModelEditHandler.post / post_keys :  %s", post_keys ) 
		# print post_keys

		# clean post args from _xsrf
		del raw_updated_fields['_xsrf']
		app_log.info("DataModelEditHandler.post / raw_updated_fields : \n %s ", pformat(raw_updated_fields) )
		# pprint.pprint( raw_updated_fields )
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
			field["_id"] 		= ObjectId(field["_id"])
			field["is_visible"] = True
		app_log.info("DataModelEditHandler.post / updated_fields : \n %s ", pformat(updated_fields) )
		# pprint.pprint(updated_fields)


		### DELETE / UPDATE FIELDS

		# first : update fields in DB
		app_log.info("DataModelEditHandler.post / updating fields ... " )
		operations =[ UpdateOne( 
			{"_id" : field["_id"]},
			{'$set':  { 
					"field_type" 	: field["field_type"],
					"field_name" 	: field["field_name"],
					"field_open" 	: field["field_open"],
					"is_visible" 	: True,
					"modified_by"	: self.get_current_user_email(),
					"modified_at"	: timestamp
					 } 
			}, 
			upsert=True ) for field in updated_fields 
		]
		self.application.coll_model.bulk_write(operations)

		# then : delete fields in db 
		app_log.info("DataModelEditHandler.post / deleting fields ...  ")
		for field in updated_fields :
			if field["field_keep"] == "delete" :
				# field_in_db = self.application.coll_model.find_one({"_id" : field["_id"]})
				# print field_in_db
				self.application.coll_model.delete_one({"_id" : field["_id"]})
				# coll_model.remove({"_id" : field["_id"]})
			if field["field_keep"] == "not visible":
				self.application.coll_model.update_one({"_id" : field["_id"]}, {"$set" : { "is_visible" : False }})
				
		### redirect once finished
		self.redirect("/datamodel/view")


class DataModelAddFieldHandler(BaseHandler) : 
	"""
	Add a new field to your data model 
	"""
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def get(self) : 

		print "\nDataModelAddFieldHandler.get... "

		self.site_section = "datamodel"

		# catch error message if any
		self.catch_error_message()


		# redirect if user doesn't have adapted auth level
		auth_level = self.user_auth_level_dict[self.site_section]
		self.redirect_user_if_not_authorized(auth_level, self.site_section)


		self.render(
			"datamodel_new_field.html",
			page_title 			= app_main_texts["main_title"],
			site_section		= self.site_section,
			field_types			= DATAMODEL_FIELDS_TYPES,
			field_open_vars		= DATAMODEL_FIELD_OPEN_VARS,
			error_msg			= self.error_msg,
			
			user				= self.current_user,
			is_user_connected 	= self.is_user_connected,
			user_email			= self.user_email,
			user_auth_level		= self.user_auth_level,		
			user_auth_level_dict = self.user_auth_level_dict,
		)

	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def post(self):

		print "\nDataModelAddFieldHandler.post ..."
		
		timestamp			= time.time()

		### TO DO : form validation
		print "DataModelAddFieldHandler.post / request.arguments ... "
		
		# print self.request 
		pprint.pprint( self.request.arguments )

		### add field to datamodel 
		
		# add complementary infos to create a full field
		new_field = {
			"field_name" 	: self.get_argument("field_name"),
			"field_type" 	: self.get_argument("field_type"),
			"field_open" 	: self.get_argument("field_open"),
			"added_at"		: timestamp,
			"added_by" 		: self.get_current_user_email(),
			"field_class" 	: "custom",
			"is_visible" 	: True,
		}
		print "DataModelAddFieldHandler.post / new_field : ", new_field

		### insert new field to db
		self.application.coll_model.insert_one(new_field)


		self.redirect("/datamodel/edit")



### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### CONTRIBUTOR lists / edit handlers #######################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class ContributorsHandler(BaseHandler): #(tornado.web.RequestHandler):
	"""
	list all contributors from db.contributors
	"""
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	# @tornado.web.asynchronous
	# @gen.coroutine
	def get(self, slug=None):

		app_log.info("ContributorsHandler.get ...\n")

		app_log.info("ContributorsHandler.get / slug : %s", slug )

		self.site_section = "contributors"

		# catch error message if any
		self.catch_error_message()


		# redirect if user doesn't have adapted auth level
		auth_level = self.user_auth_level_dict[self.site_section]
		self.redirect_user_if_not_authorized(auth_level, self.site_section)


		# get current page 
		current_page = self.get_current_uri_without_error_slug()
		app_log.info("ContributorsHandler.get / current_page : %s", current_page )

		# get slug args
		slug_ = self.request.arguments
		app_log.info("ContributorsHandler.get / slug_ : \n %s", pformat(slug_) )

		# filter slug
		query_contrib = self.filter_slug( slug_, slug_class="contributors" )
		app_log.info("ContributorsHandler.get / query_contrib : \n %s ", pformat(query_contrib) )

		# get data 
		contributors, is_data, page_n_max, count_results_tot, query = self.get_data_from_query( query_contrib, coll_name="contributors", sort_by="infos.name")
		
		if len(contributors) != 0 : 
			app_log.info("ContributorsHandler.get / contributors[0] : \n %s " , pformat(contributors[0]) )
			print '.....\n'

		# count docs by spider_id
		count_docs_by_spiders = self.count_docs_by_field(coll_name="data", field_name="spider_id")
		app_log.info("count_docs_by_spiders : \n %s",  pformat(count_docs_by_spiders) )

		### operations if there is data
		pagination_dict = None
		if is_data : 
			
			app_log.info("ContributorsHandler.get / is_data : %s ", is_data ) 
			
			# make pagination 
			pagination_dict = self.wrap_pagination( 
									page_n		= query_contrib["page_n"], 
									page_n_max	= page_n_max
								)
			app_log.info("ContributorsHandler / pagination_dict : \n %s ", pformat(pagination_dict) )

		self.render("contributors_view.html",
			
			page_title  			= app_main_texts["main_title"],
			site_section			= self.site_section, 
			current_page			= current_page,

			query_obj				= query_contrib,
			contributors 			= contributors,
			is_contributors 		= is_data,
			count_docs_by_spiders 	= count_docs_by_spiders,

			pagination_dict			= pagination_dict,
			error_msg				= self.error_msg,
			
			user					= self.current_user,
			is_user_connected 		= self.is_user_connected,
			user_email				= self.user_email,
			user_auth_level			= self.user_auth_level,
			user_auth_level_dict 	= self.user_auth_level_dict,

		)


class ContributorEditHandler(BaseHandler): #(tornado.web.RequestHandler):
	"""
	contributor edit handler
	"""

	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def get(self, spider_id=None):
		"""show infos on one contributor : get info in DB and prefill form"""
		
		print
		app_log.info("ContributorEditHandler.get / spider_id : {}".format( spider_id ) )

		self.site_section = "contributors"


		### check user auth level 
		# redirect if user doesn't have adapted auth level
		auth_level = self.user_auth_level_dict[self.site_section]
		self.redirect_user_if_not_authorized(auth_level, self.site_section)



		# catch error message if any
		self.catch_error_message()

		### retrieve datamodel - custom fields
		data_model_custom = list(self.application.coll_model.find( {"field_class" : "custom"})) #, {"field_name":1, "_id":1} ))
		app_log.info( "\n %s", pformat(data_model_custom) )


		data_model_custom = [ { k : unicode(v) for k,v in i.iteritems() } for i in data_model_custom ]

		contributor_edit_fields = CONTRIBUTOR_EDIT_FIELDS


		### retrieve contributor data from spider_id
		# spider exists ( edit form ) 
		if spider_id != None :
			try : 
				create_or_update	= "update"
				contributor			= self.application.coll_spiders.find_one({"_id": ObjectId(spider_id)})
			except :
				app_log.warning("ContributorEditHandler.get --- !!! spider_id -%s- not found", spider_id ) 
				
				self.error_msg = self.add_error_message_to_slug( 
									error_string="there is no spider configuration with -%s- spider_id in the DB" %(str(spider_id)),
									)
				self.redirect("/contributors" + self.error_msg)

		# spider doesn't exist : add form
		else :
			# core empty contributor structure to begin with
			contributor_object 	= SpiderConfig(user=self.user_email, new_spider=True)
			contributor 		= contributor_object.full_config_as_dict()
			create_or_update	= "create"

		print
		app_log.info( "ContributorEditHandler.get / contributor : \n %s", pformat(contributor))

		### render page
		# self.render("contributor_edit.html",
		self.render("contributor_edit_accordion.html",
			
			page_title 				= app_main_texts["main_title"],
			site_section			= self.site_section,
			
			create_or_update 		= create_or_update,
			
			contributor_edit_fields 		= contributor_edit_fields,
			contributor_edit_radio 			= CONTRIBUTOR_EDIT_FIELDS_RADIO,
			contributor_edit_radio_texts	= CONTRIBUTOR_EDIT_FIELDS_RADIO_TEXTS,
			contributor_edit_numbers 		= CONTRIBUTOR_EDIT_FIELDS_NUMBER,
			contributor_edit_floats 		= CONTRIBUTOR_EDIT_FIELDS_FLOAT,
			contributor 					= contributor,
			
			datamodel				= data_model_custom,
			error_msg				= self.error_msg,
			
			user				= self.current_user,
			is_user_connected 	= self.is_user_connected,
			user_email			= self.user_email,
			user_auth_level		= self.user_auth_level,
			user_auth_level_dict = self.user_auth_level_dict,
			
		)


	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def post(self, spider_id=None):
		"""update or create new contributor spider in DB"""

		print
		app_log.info( "ContributorEditHandler.post... spider_id : %s ", spider_id )
		
		timestamp = time.time()
		




		### TO DO : form validation
		

		### get form back from client
		spider_config_form = self.request.arguments
		app_log.info("ContributorEditHandler.post /spider_config_form : \n %s", pformat(spider_config_form) )


		# check if spider already exists
		is_new = True
		if spider_id != None : 
			spider_id = spider_config_form["_id"][0]
			is_new = False

		# check if website is already crawled by another spider
		similar_spider = self.application.coll_spiders.find_one( {"infos.page_url": spider_config_form["page_url"][0] } ) 
		app_log.info("ContributorEditHandler.post /similar spider : \n %s", pformat(similar_spider) )

		if similar_spider and is_new and spider_config_form != "" :
			app_log.warning( "ContributorEditHandler.post / a similar spider already exists ... ")
			
			# TO DO : add alert
			self.error_slug = self.add_error_message_to_slug("this website is already being scraped by {}".format( similar_spider["infos"]["name"]) )
			self.redirect("/contributors" + self.error_slug )

		else : 
			# populate a contributor object
			print
			app_log.info( "ContributorEditHandler.post / creating spider with SpiderConfig class  ... ")
			contributor_object = SpiderConfig( 
					form 		= spider_config_form,
					new_spider 	= is_new,
					user		= self.get_current_user_email() 
			)

			### get spider identifier from form
			app_log.info( "ContributorEditHandler.post / spider_config_form : \n %s", pformat(spider_config_form) )

			if spider_id and spider_id != "new_spider":
				
				app_log.warning( "ContributorEditHandler.post / spider_id %s already exists : ", spider_id )

				# getting id from form
				spider_oid = ObjectId(spider_id)

				# getting back spider config from db but from its _id
				contributor = self.application.coll_spiders.find_one( {"_id": ObjectId(spider_oid)} )
				new_config 	= contributor_object.partial_config_as_dict( previous_config = contributor )

				# update contributor
				old_fields = {"infos" : 1 , "scraper_config" : 1 , "scraper_config_xpaths" : 1, "scraper_settings" : 1 }
				self.application.coll_spiders.update_one( {"_id": spider_oid}, { "$unset": old_fields } )
				self.application.coll_spiders.update_one( {"_id": spider_oid}, { "$set"	 : new_config }, upsert=True )

				# update contributor 
				self.update_spider_log(spider_id=spider_id, spider_oid=spider_oid, log_to_update="is_data_available",	value=False)
				self.update_spider_log(spider_id=spider_id, spider_oid=spider_oid, log_to_update="is_tested", 			value=False)


			else :
				contributor = contributor_object.full_config_as_dict()
				# insert new spider to db
				self.application.coll_spiders.insert_one(contributor)

			print 
			app_log.info( "ContributorEditHandler.post / contributor : \n %s ", pformat(contributor) ) 

			
			### redirection
			self.redirect("/contributors")


class ContributorDeleteHandler(BaseHandler) : 
	"""
	completly delete a spider configuration from db
	"""
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def get(self):
		
		print
		app_log.warning("ContributorDeleteHandler.get / contributors :")

		# catch error if any
		self.catch_error_message()

		self.site_section = "contributors"

		# redirect if user doesn't have adapted auth level
		auth_level = self.user_auth_level_dict[self.site_section]
		self.redirect_user_if_not_authorized(auth_level, self.site_section)


		spider_id = self.get_argument('spider_id', None )
		app_log.info("ContributorDeleteHandler.get / spider_id : %s", spider_id )

		spider_oid = ObjectId(spider_id)

		# spider exists ( edit form ) 
		if spider_id :
			
			try : 
				contributor	= self.application.coll_spiders.find_one({"_id": spider_oid })
			
				self.render( "contributor_delete.html",
					
					page_title  			= app_main_texts["main_title"],
					# site_section			= self.site_section, 

					spider_id				= spider_id,
					contributor				= contributor,

					error_msg				= self.error_msg,
					
					user				= self.current_user,
					is_user_connected 	= self.is_user_connected,
					user_email			= self.user_email,
					user_auth_level		= self.user_auth_level,
					user_auth_level_dict = self.user_auth_level_dict,
				)

			except :
				app_log.warning("ContributorDeleteHandler.get --- !!! spider_id -%s- not found", spider_id ) 
				
				self.error_msg = self.add_error_message_to_slug( 
									error_string	= "there is no spider configuration with -%s- spider_id in the DB" %(str(spider_id)),
									args_to_delete 	= QUERY_SPIDER_BY_DEFAULT.keys()
									)
				self.redirect("/contributors" + self.error_msg)


		else :
			self.redirect("/contributors")


	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def post(self):

		print 
		app_log.info("ContributorDeleteHandler.post ... " )
		app_log.info("ContributorDeleteHandler.post / request.arguments : \n %s ", pformat(self.request.arguments ) )


		# TO DO : form validation 

		### get reset choice + data validation
		spider_id	= self.get_argument("spider_id")
		app_log.info("ContributorDeleteHandler.post / spider_id : %s", spider_id )

		spider_oid = ObjectId(spider_id)

		is_delete	= self.get_argument("is_delete")
		app_log.info("ContributorDeleteHandler.post / is_delete : %s", is_delete )
		
		# reset collection here
		if is_delete == "true" :

			app_log.warning("ContributorDeleteHandler.post / DELETING SPIDER FOR spider_id : %s", spider_id )
			self.application.coll_spiders.delete_one({ "_id" : spider_oid })

			self.error_msg = self.add_error_message_to_slug( 
								error_string	= "the spider was erased",
								args_to_delete 	= QUERY_SPIDER_BY_DEFAULT.keys()
								)
			
			self.redirect("/contributors" + self.error_msg )

		else :
			self.redirect("/contributors")


class ContributorResetDataHandler(BaseHandler) : 
	"""
	delete a spider config
	"""
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def get(self):

		print
		app_log.info("ContributorResetDataHandler.get ..." )

		# catch error if any
		self.catch_error_message()

		self.site_section = "contributors"

		# redirect if user doesn't have adapted auth level
		auth_level = self.user_auth_level_dict[self.site_section]
		self.redirect_user_if_not_authorized(auth_level, self.site_section)


		spider_id = self.get_argument('spider_id', None )
		app_log.info("ContributorResetDataHandler.get / spider_id : %s", spider_id )

		spider_oid = ObjectId(spider_id)

		# spider exists ( edit form ) 
		if spider_id :
			
			try : 
				contributor	= self.application.coll_spiders.find_one({"_id": spider_oid })

				# redirect
				self.render(
					"contributor_reset_data.html",
					page_title  			= app_main_texts["main_title"],
					# site_section			= self.site_section, 

					spider_id				= spider_id,
					contributor				= contributor,

					error_msg				= self.error_msg,
					
					user				= self.current_user,
					is_user_connected 	= self.is_user_connected,
					user_email			= self.user_email,
					user_auth_level		= self.user_auth_level,
					user_auth_level_dict = self.user_auth_level_dict,
					)
				
			except :
				app_log.warning("ContributorResetDataHandler.get --- !!! spider_id -%s- not found", spider_id ) 
				
				self.error_msg = self.add_error_message_to_slug( 
									error_string	= "there is no spider configuration with -%s- spider_id in the DB" %(str(spider_id)),
									args_to_delete 	= QUERY_SPIDER_BY_DEFAULT.keys()
									)
				self.redirect("/contributors" + self.error_msg)

		else :
			self.redirect("/contributors")



	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@check_user_permissions
	def post(self):

		print 
		app_log.info("ContributorResetDataHandler.post ... " )

		app_log.info("ContributorResetDataHandler.post / request.arguments : \n %s ", pformat(self.request.arguments ) )

		# TO DO : form validation 

		### get reset choice + data validation
		spider_id	= self.get_argument("spider_id")
		app_log.info("ContributorResetDataHandler.post / spider_id : %s", spider_id )
		
		spider_oid = ObjectId(spider_id)

		is_reset	= self.get_argument("reset_data")
		app_log.info("ContributorResetDataHandler.post / is_reset : %s", is_reset )
		
		# reset collection here
		if is_reset == "true" :

			contributor	= self.application.coll_spiders.find_one({"_id": spider_oid })

			app_log.warning("ContributorResetDataHandler.post / DELETING DOCUMENTS IN COLL_DATA for spider_id : %s", spider_id )
			self.application.coll_data.delete_many({ "spider_id" : spider_id })
			
			# add warning message (as error for now)
			self.error_msg = self.add_error_message_to_slug( 
								error_string	= "all data from -%s- were erased" %(contributor["infos"]["name"]),
								args_to_delete 	= QUERY_SPIDER_BY_DEFAULT.keys()
								)

			# update scraper log
			self.update_spider_log(spider_id=spider_id, spider_oid=spider_oid, log_to_update="is_data_available", value=False)

			# redirect
			self.redirect("/contributors" + self.error_msg )

		else : 
			self.redirect("/contributors")





### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### DATA lists / edit handlers ##############################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

### TO DO - after item pipeline

class DataScrapedHandler(BaseHandler):
	"""
	list all data scraped from db.data_scraped 
	"""
	@print_separate(APP_DEBUG)
	@check_user_permissions
	def get (self, slug ):
		
		print
		app_log.info("DataScrapedHandler.get ... : \n")

		self.site_section = "data"

		# catch error message if any
		self.catch_error_message()

		# print "\nDataScrapedHandler.get / slug : "
		# pprint.pprint(slug)

		app_log.info("DataScrapedHandler.get / request : " )
		pprint.pprint (self.request )

		print
		app_log.info("DataScrapedHandler.get ... : ")
		app_log.info("... request.path : %s ", self.request.path )
		app_log.info("... request.uri  : %s ", self.request.uri )





		### SPIDERS 

		### retrieve all spiders from db to make correspondances spider_id --> spider_name
		spiders_list = list( self.application.coll_spiders.find( {}, {"infos" : 1 } ) )
		spiders_dict = {}
		
		if len(spiders_list) > 0 :
			app_log.info("DataScrapedHandler.get / spiders_list[0] :")
			pprint.pprint (spiders_list[0])
			print "..."

			# make a dict from spiders_list to make correspondances spider_id --> spider_name
			spiders_dict = { str(s["_id"]) : s["infos"]["name"] for s in spiders_list }
			app_log.info("DataScrapedHandler.get / spiders_dict :\n %s ", pformat(spiders_dict) )  





		### DATA QUERY 

		slug_ = self.request.arguments
		print
		app_log.info("DataScrapedHandler.get / slug_ : %s ", slug_ )

		### clean slug as data query
		query_data = self.filter_slug( slug_, slug_class="data", query_from="app" )
		app_log.info("DataScrapedHandler / query_data : \n %s ", pformat(query_data) )

		# get export_as_csv arg
		export_as_csv = query_data["export_as_csv"]
		app_log.info("DataScrapedHandler.get / export_as_csv : %s", export_as_csv)



		open_level = self.user_auth_level_dict["data"] # generated by @check_request_token
		app_log.info("DataScrapedHandler / open_level : %s ", open_level )


		### TO DO : FACTORIZE WITH APIrestHandler HANDLER
		dm_set = self.get_datamodel_set()
		data_model_custom_list		 	= dm_set["data_model_custom_list"]
		data_model_custom_dict 		 	= dm_set["data_model_custom_dict"]
		data_model_custom_dict_names 	= dm_set["data_model_custom_dict_names"]
		data_model_core_list		 	= dm_set["data_model_core_list"]
		data_model_core_dict_names		= dm_set["data_model_core_dict_names"]


		### retrieve datamodel from DB top make correspondances field's _id --> field_name
		# data_model_custom = list( self.application.coll_model.find({"field_class" : "custom", "is_visible" : True }).sort("field_name",1) )
		# app_log.info("DataScrapedHandler.get / data_model_custom[:2] :" )
		# pprint.pprint (data_model_custom[:2] )
		# print "..."

		data_model_custom_ids = [ str(dmc["_id"]) for dmc in data_model_custom_list ]
		app_log.info("DataScrapedHandler.get / data_model_custom_ids[:2] : \n %s ", data_model_custom_ids[:2] )
		# pprint.pprint (data_model_custom_ids[:2])
		print "..."

		# data_model_core = list( self.application.coll_model.find({"field_class" : "core"})  )

		### filter results depending on field's opendata level
		# get fields allowed
		allowed_fields_list, allowed_custom_fields, allowed_core_fields = self.get_authorized_datamodel_fields(open_level, data_model_custom_list, data_model_core_list )
		allowed_fields_list.append("spider_id")
		app_log.info("DataScrapedHandler.get / allowed_fields_list : \n %s ", allowed_fields_list ) 






		### get items from db
		items_from_db, is_data, page_n_max, count_results_tot, query = self.get_data_from_query( 	query_data, 
																		coll_name						= "data", 
																		query_from						= self.site_section, 
																
																		allowed_fields_list				= allowed_fields_list,
																		ignore_fields_list				= ["_id"],

																		data_model_custom_dict			= data_model_custom_dict, 
																		# data_model_custom_dict_names = data_model_custom_dict_names,
																		# data_model_core_dict_names	 = data_model_core_dict_names
																	)



		### operations if there is data
		pagination_dict = None
		if is_data : 
			
			# make pagination 
			pagination_dict = self.wrap_pagination( 
									page_n		= query_data["page_n"], 
									page_n_max	= page_n_max
								)
			print
			app_log.info("DataScrapedHandler / pagination_dict : \n %s ", pformat(pagination_dict))

			# clean items 
			for item in items_from_db : 
				# put spider name instead of spider _id
				item["spider_name"] = spiders_dict[ item["spider_id"] ]

			print 
			app_log.info("DataScrapedHandler / items_from_db[0] : \n %s ", pformat(items_from_db[0]) )
			print "..."



		if export_as_csv == False : 

			app_log.info("DataScrapedHandler / serve html...")

			self.render(
				"data_view.html",
				page_title			= app_main_texts["main_title"],
				query_obj			= query_data,
				
				datamodel_custom 	  = data_model_custom_list,
				allowed_custom_fields = allowed_custom_fields,

				# spiders_list		= spiders_list,
				items				= items_from_db,
				is_data				= is_data,
				pagination_dict		= pagination_dict,
				site_section		= self.site_section,
				error_msg			= self.error_msg,
				
				user				= self.current_user,
				is_user_connected 	= self.is_user_connected,
				user_email			= self.user_email,
				user_auth_level		= self.user_auth_level,		
				user_auth_level_dict = self.user_auth_level_dict,
			)
		
		else : 
			app_log.info("DataScrapedHandler / export results as csv...")

			spider_id_string_list = query_data["spider_id"]
			spider_id_string_list = "_".join(spider_id_string_list)

			# cf : https://stackoverflow.com/questions/43920868/how-to-specify-csv-file-encoding-when-downloading-it-with-tornado-in-python
			filename = "export_openscraper_{}.csv".format(spider_id_string_list)
			self.set_header('Content-Type', "text/csv; charset=UTF-8")
			self.set_header('Content-Disposition', 'attachment; filename=' + filename)
			
			### TO DO 

			### cf : check data_view.html to see how to map fields and items' values 

			### clean fields to keep 
			app_log.info("DataScrapedHandler / export csv / data_model_custom_list[:2] ...")
			pprint.pprint(data_model_custom_list[:2])
			print "..."
			csv_headers = ["spider_name", "link_src", "link_data"] 
			for field in data_model_custom_list :
				id_field 	= str(field[u"_id"])
				if id_field in allowed_custom_fields :
					csv_headers.append(field['field_name'])
			app_log.info("DataScrapedHandler / export csv / csv_headers ...")
			pprint.pprint(csv_headers)
			titles = '|'.join(csv_headers)
			self.write(titles.encode("UTF-8"))

			### clean items_from_db to flat list of items values
			app_log.info("DataScrapedHandler / export csv / items_from_db[:2] ...")
			pprint.pprint(items_from_db[:2])
			print "..."
			for item in items_from_db :
				item_list = [ 
					item["spider_name"], 
					item["link_src"],
				]
				item_list.append(item["link_data"] if "link_data" in item.keys() else '')
				for field in data_model_custom_list :
					id_field 	= str(field[u"_id"])
					if id_field in allowed_custom_fields : 
						type_field 	= str(field[u"field_type"])
						if id_field in item.keys() :
							item_list.append( " ".join(item[ id_field ]) )
				csv_item = '\n'+'|'.join(item_list)
				self.write(csv_item.encode("UTF-8"))
			





# class DataScrapedViewOneHandler(BaseHandler):
# 	"""
# 	list all data scraped from db.data_scraped 
# 	"""
# 	@print_separate(APP_DEBUG)
# 	def get (self, spidername=None):
# 		self.redirect("/404")



### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### AJAX handler ############################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

# cf : https://stackoverflow.com/questions/23984586/reply-to-ajax-request-using-tornado
# cf : https://gist.github.com/mminer/5464753

# cf : https://github.com/richstoner/TornadoAJAXSample/blob/master/templates/index.html
# cf : https://github.com/richstoner/TornadoAJAXSample/blob/master/app.py

class AjaxHandler(BaseHandler):
	"""Simple, ajax handler"""
	
	def get(self, *args, **kwargs):
		"""get unlikely to be used for ajax"""
		self.write("Not allowed")
		self.finish()

	def post(self, *args):
		"""Example handle ajax post"""
		dic = tornado.escape.json_decode(self.request.body)
		app_log.info("ajax / dic : \n %s " , pformat(dic) )

		# useful code goes here
		
		self.write(json.dumps({'status': 'ok', 'sent': dic}))
		self.finish()




### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### INFOS / DOC  ############################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class WhoHandler(BaseHandler) : 
	"""
	"""
	@print_separate(APP_DEBUG)
	def get(self):

		app_log.info("WhoHandler.get... ")

		self.render(
			"who.html",
			page_title 				= app_main_texts["main_title"],
			user					= self.current_user,
			is_user_connected 		= self.is_user_connected,
			user_email				= self.user_email,
			user_auth_level			= self.user_auth_level,
			user_auth_level_dict 	= self.user_auth_level_dict,
		)

class TutoHandler(BaseHandler) : 
	"""
	"""
	@print_separate(APP_DEBUG)
	def get(self):

		app_log.info("TutoHandler.get... ")

		self.render(
			"tuto.html",
			page_title 				= app_main_texts["main_title"],
			user					= self.current_user,
			is_user_connected 		= self.is_user_connected,
			user_email				= self.user_email,
			user_auth_level			= self.user_auth_level,
			user_auth_level_dict 	= self.user_auth_level_dict,
		)

class APIdocHandler(BaseHandler) : 
	"""
	"""
	@print_separate(APP_DEBUG)
	def get(self):

		app_log.info("APIdocHandler.get... ")

		self.render(
			"api_doc.html",
			page_title 				= app_main_texts["main_title"],
			user					= self.current_user,
			is_user_connected 		= self.is_user_connected,
			user_email				= self.user_email,
			user_auth_level			= self.user_auth_level,
			user_auth_level_dict 	= self.user_auth_level_dict,
		)

### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### SNIPPETS handlers #######################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class FormHandler(BaseHandler) : 
	"""
	test with basic Bulma Form
	"""
	@print_separate(APP_DEBUG)
	@check_user_permissions
	def get(self):

		print "\FormHandler.get... "

		form = SampleForm()

		if form.validate():
			# do something with form.username or form.email
			pass

		self.render(
			"form_instance.html",
			page_title 			= app_main_texts["main_title"],
			form 				= form,

			user					= self.current_user,
			is_user_connected 		= self.is_user_connected,
			user_email				= self.user_email,
			user_auth_level			= self.user_auth_level,
			user_auth_level_dict 	= self.user_auth_level_dict,

		)

	@print_separate(APP_DEBUG)
	def post(self):
		
		print "\FormHandler.post... "

		### get form back from client
		form = SampleForm(self.request.arguments)
		print "\nFormHandler.post / spider_config_form : "
		pprint.pprint( form )


class TestBulmaHandler(BaseHandler) : 
	"""
	test with basic Bulma extensions
	"""
	@print_separate(APP_DEBUG)
	@check_user_permissions
	def get(self):

		print
		app_log.info("TestBulmaHandler.get... ")

		self.render(
			"test_bulma_extensions.html",
			page_title 				= app_main_texts["main_title"],
			user					= self.current_user,
			is_user_connected 		= self.is_user_connected,
			user_email				= self.user_email,
			user_auth_level			= self.user_auth_level,
			user_auth_level_dict 	= self.user_auth_level_dict,
		)





### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### TORNADO MODULES #########################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class PaginationModule(tornado.web.UIModule):
	"""
	module for pagination
	"""
	def render( self, pagination_dict ):
		return self.render_string(
			"modules/mod_pagination.html", 
			pagination_dict = pagination_dict,
		)

class MainTabsModule(tornado.web.UIModule):
	"""
	module for main tabs
	"""
	def render( self, site_section ):
		return self.render_string(
			"modules/mod_tabs.html", 
			site_section = site_section,
		)

class ErrorModalModule(tornado.web.UIModule):
	"""
	module for error messages
	"""
	def render( self, error_msg ):
		return self.render_string(
			"modules/mod_error_modal.html", 
			error_msg = error_msg,
		)

	def javascript_files(self):
		return "js/modal_error.js"

	# def css_files(self):
	# 	return "css/recommended.css"
