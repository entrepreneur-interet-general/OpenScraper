# -*- encoding: utf-8 -*-


import 	pprint 
from 	pprint import pprint, pformat
import 	math
import	urllib
from 	copy import deepcopy

import 	time
from 	bson import ObjectId
from 	datetime import datetime
from 	functools import wraps

import 	jwt

import pymongo
# from 	pymongo import UpdateOne


import 	tornado.web, tornado.escape #, tornado.template,
from	tornado.log import access_log, app_log, gen_log

# threading for background tasks (spiders mainly)
# cf : https://stackoverflow.com/questions/22082165/running-an-async-background-task-in-tornado/25304704
# cf : https://gist.github.com/marksilvis/ea1142680db66e2bb9b2a29e57306d76

# import toro # deprecated it seems
# from 	tornado.ioloop import IOLoop
from 	tornado import gen, concurrent
# from 	tornado.concurrent import return_future, run_on_executor

from 	concurrent.futures import ThreadPoolExecutor # need to install futures in pytohn 2.7
from 	handler_threading import *


### import app settings / infos 
from config.app_infos 			import app_infos, app_main_texts
from config.settings_example 	import * # MONGODB_COLL_CONTRIBUTORS, MONGODB_COLL_DATAMODEL, MONGODB_COLL_DATASCRAPPED
from config.settings_corefields import * # USER_CORE_FIELDS, etc...
from config.settings_queries 	import * # QUERY_DATA_BY_DEFAULT, etc...
from config.core_classes		import * # SpiderConfig, UserClass, QuerySlug
from config.settings_threading	import * # THREADPOOL_MAX_WORKERS, etc...
from config.settings_cleaning	import * # STRIP_STRING, DATA_CONTENT_TO_IGNORE, etc...
from config.settings_errors		import * # REDIRECT_TO_IF_NOT_AUTHORIZED, etc...




### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### DECORATOR handler for all routing handlers ##############################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

### NOT FULLY TESTED YET / BASED ON tornado.web.authenticated

def check_user_permissions(method):
	"""
	Decorate methods with this to require that the user 
	have the correct email to be able to modify stuff like the datamodel or a spider
	"""
	@wraps(method)
	def wrapper(self, *args, **kwargs):

		print
		app_log.info(" ... check_user_permissions ... ")
		app_log.info(" ... check_user_permissions / self.request.full_url() : \n %s ", self.request.full_url())

		# override default user_email value
		self.user_email = self.get_current_user_email()

		user_auth_level = self.get_current_user_auth_level()
		app_log.info(" ... check_user_permissions / user_auth_level : %s ",user_auth_level )
		
		user_auth_level_dict = USER_AUTH_LEVELS[user_auth_level]
		app_log.info(" ... check_user_permissions / auth_level : %s ", user_auth_level_dict )

		# override default user_auth_level and user_auth_level_dict
		self.user_auth_level 		= user_auth_level
		self.user_auth_level_dict 	= user_auth_level_dict

		app_log.info("... check_user_permissions / self.user_auth_level      : %s ...", self.user_auth_level  )
		app_log.info("... check_user_permissions / self.user_auth_leve_dictl : %s ...", pformat( self.user_auth_level_dict)  )
		
		# if not self.current_user:

		# 	if self.request.method in ("GET", "HEAD"):
		# 		url = self.get_login_url()
		# 		if "?" not in url:
		# 			if urlparse.urlsplit(url).scheme:
		# 				# if login url is absolute, make next absolute too
		# 				next_url = self.request.full_url()
		# 			else:
		# 				next_url = self.request.uri
		# 			url += "?" + urlencode(dict(next=next_url))
		# 		self.redirect(url)
		# 		return

		# 	raise HTTPError(403)

		print

		return method(self, *args, **kwargs)
	return wrapper


def check_request_token(method) : 
	"""
	Decorate methods with this to require that the user 
	have the correct email to be able to modify stuff like the datamodel or a spider
	"""
	@wraps(method)
	def wrapper(self, *args, **kwargs):

		print
		app_log.info(" ... check_request_token ... ")
		app_log.info(" ... check_request_token / self.request.full_url() : \n %s ", self.request.full_url())

		### get token 
		slug_ = self.request.arguments
		token = slug_.get("token", None)
		# if no token in slug try getting it from post header ? 

		app_log.info(" ... check_user_permissions / token 			: %s ", token )


		### get user_auth_level
		if token == None : 
			user_auth_level = "visitor"
		else :
		

			### TO DO : decrypt token instead of default 
			user_auth_level = "user"
			self.user_email = "default.api.email@openscraper.com"
		



		app_log.info(" ... check_user_permissions / user_auth_level : %s ", user_auth_level )
		
		### get user_auth_level_dict
		user_auth_level_dict = USER_AUTH_LEVELS[user_auth_level]
		app_log.info(" ... check_user_permissions / user_auth_level_dict : %s ", user_auth_level_dict )

		### add to base handler
		self.user_auth_level 		= user_auth_level
		self.user_auth_level_dict 	= user_auth_level_dict

		app_log.info("... check_user_permissions / self.user_auth_level      : %s ...", self.user_auth_level  )
		app_log.info("... check_user_permissions / self.user_auth_leve_dictl : %s ...", pformat( self.user_auth_level_dict)  )
		
		# if not self.current_user:

		# 	if self.request.method in ("GET", "HEAD"):
		# 		url = self.get_login_url()
		# 		if "?" not in url:
		# 			if urlparse.urlsplit(url).scheme:
		# 				# if login url is absolute, make next absolute too
		# 				next_url = self.request.full_url()
		# 			else:
		# 				next_url = self.request.uri
		# 			url += "?" + urlencode(dict(next=next_url))
		# 		self.redirect(url)
		# 		return

		# 	raise HTTPError(403)

		print

		return method(self, *args, **kwargs)
	return wrapper





### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### BASE handler for all routing handlers ###################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
"""
SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PATCH", "PUT", "OPTIONS")
"""

class BaseHandler(tornado.web.RequestHandler):
	"""
	Base class for all routes/handlers : 
	each handler wil inheritate those following functions if writtent like this
	MyNewHandler(BaseHandler)
	"""

	### global executor for base handler to deal with @run_on_executor

	executor = ThreadPoolExecutor(max_workers=THREADPOOL_MAX_WORKERS)



	### global settings at init handler

	def __init__(self, *args, **kwargs) : 
		
		### super init/override tornado.web.RequestHandler with current args 

		super(BaseHandler, self).__init__(*args, **kwargs)

		app_log.info("--- BaseHandler / __init__ : \n")
		# app_log = self.application.gen_log

		### global vars for every handler
		self.is_user_connected	 	= self.get_if_user_connected()
		self.error_msg	 			= ""
		self.site_section 			= ""

		self.user_auth_level		= "visitor"
		self.user_auth_level_dict 	= USER_AUTH_LEVELS[self.user_auth_level]

		self.user_email				= "visitor.email@openscraper.com"

	### global functions for all handlers

	def catch_error_message (self):
		""" get and log error message if any """
		
		try:
			self.error_msg = self.get_argument("error")
			app_log.warning("\n... get_error_message / self.error_msg : %s ", self.error_msg )
		
		except:
			self.error_msg = ""

	def add_error_message_to_slug(self, error_string, args_to_delete=[], msg_categ="error" ) : 
		""" add an "error" arg to url slug """

		slug_ = self.request.arguments
		app_log.info("... add_error_message_to_slug / slug_ : \n %s ", pformat( slug_ ) )

		# create a complete clean slug if no slug
		if slug_ == {} :
			error_slug = u"?" + u"error=" + tornado.escape.url_escape(error_string)
		
		# add error arg to existing slug
		else : 

			slug_without_error = deepcopy(slug_)			

			### clean existing slug from existing error arg if any
			# for arg_to_delete in args_to_delete + DEFAULT_ERROR_ARGS_TO_DELETE : 
			# 	try : 
			# 		del slug_without_error[arg_to_delete]
			# 	except :
			# 		pass
			slug_without_error = self.clean_slug(slug_without_error, args_to_delete + DEFAULT_ERROR_ARGS_TO_DELETE )

			app_log.warning("... add_error_message_to_slug / slug_without_error : \n %s ", pformat(slug_without_error) )

			# recreate slug
			error_dict	= { "error" : error_string }
			error_dict.update( slug_without_error )
			error_slug = u"?" + urllib.urlencode( error_dict, doseq=True)		

		app_log.info("... add_error_message_to_slug / error_slug : \n %s ", pformat(error_slug) )

		return error_slug

	def clean_slug(self, slug, args_list_to_delete=[]) :
		""" clean slug from unwanted args """

		print 
		app_log.info("... clean_slug ..."  )
		app_log.info("... clean_slug / slug : %s "					, slug  )
		app_log.info("... clean_slug / args_list_to_delete : %s "	, args_list_to_delete  )

		# slug 		= self.request.arguments

		for arg_to_delete in args_list_to_delete : 
			
			try : 
				del slug[arg_to_delete]
			except :
				pass

		print 

		return slug

	def wrap_pagination (self, page_n, page_n_max ):
		""" wrap all pagination args in a dict """

		print
		app_log.info("... wrap_pagination : ... ")
		app_log.info("... wrap_pagination / request.path : %s ", self.request.path )

		slug_ = self.request.arguments
		app_log.info("... wrap_pagination / slug_ : \n %s ", pformat(slug_) )

		# copy raw slug
		slug_without_page = deepcopy(slug_)
		

		# # clean from page_n if any
		# try : 
		# 	del slug_without_page["page_n"]
		# except :
		# 	pass

		# # clean from error arg if any
		# try : 
		# 	del slug_without_page["error"]
		# except :
		# 	pass
		slug_without_page = self.clean_slug(slug_without_page, PAGINATION_ARGS_TO_IGNORE )

		app_log.info("... wrap_pagination / slug_without_page :  \n %s  ", pformat(slug_without_page) )

		# base_uri		= self.request.uri
		base_path		= self.request.path
		base_slug		= ""
		# print tornado.escape.url_unescape(self.request.uri)
		# cf : https://stackoverflow.com/questions/1233539/python-dictionary-to-url-parameters
		# print urllib.urlencode({'p': [1, 2, 3]}, doseq=True)
		if slug_without_page !={} : 
			base_slug		= "?" + urllib.urlencode( slug_without_page, doseq=True)
		app_log.info("... wrap_pagination / base_slug : \n %s ", base_slug )

		path_slug 		= base_path + base_slug
		app_log.info("... wrap_pagination / path_slug : \n %s ", path_slug )

		# recreate url strings
		first_slug	= { "page_n" : 1 }
		first_slug.update( slug_without_page )
		first_slug_s = "?" + urllib.urlencode( first_slug, doseq=True)

		prev_n 		=  page_n - 1
		prev_slug	= { "page_n" : prev_n }
		prev_slug.update( slug_without_page )
		prev_slug_s = "?" + urllib.urlencode( prev_slug, doseq=True)
		
		next_n 		=  page_n + 1
		next_slug	= { "page_n" : next_n }
		next_slug.update( slug_without_page )
		next_slug_s = "?" + urllib.urlencode( next_slug, doseq=True)
		
		last_n 		=  page_n_max
		last_slug	= { "page_n" : last_n }
		last_slug.update( slug_without_page )
		last_slug_s = "?" + urllib.urlencode( last_slug, doseq=True)

		# backbone of pagination 
		pagination 	= {
			
			"first_n"			: 1,
			"first_uri"			: base_path + first_slug_s,
			
			"prev_n" 			: page_n - 1,
			"prev_uri" 			: base_path + prev_slug_s ,
			"is_prev"			: True,

			"next_n"			: page_n + 1,
			"next_uri" 			: base_path + next_slug_s ,
			"is_next"			: True,

			"last_n"			: page_n_max,
			"last_uri"			: base_path + last_slug_s,
			"is_last"			: True,

			"current_page_n"	: page_n,

		}
			
		# handle specific cases
		if page_n <= 1 :
			pagination["is_first"] 	= False
			pagination["is_prev"] 	= False

		if page_n >= page_n_max :
			pagination["is_last"] 	= False
			pagination["is_next"] 	= False

		return pagination

	def get_current_uri_without_error_slug (self, slug_class=None) :
		""" 
		returns uri without the error slug 
		- note : duplicates a bit the work done for api sluf query
		""" 

		print 
		app_log.info("... get_current_uri_without_error_slug ..." )

		base_path 	= self.request.path
		slug 		= self.request.arguments

		# clean slug from other unwanted args 
		slug = self.clean_slug(slug, ERROR_ARGS_SPIDER_TO_IGNORE )

		# reconstruct slug without unwanted args
		if slug !={} : 
			base_slug = "?" + urllib.urlencode( slug, doseq=True)
		else : 
			base_slug = "" 

		current_uri = base_path + base_slug

		return current_uri

	def compute_count_and_page_n_max(self, results_count, limit_results) :
		
		### compute max_pages, start index, stop index
		page_n_max 		= int(math.ceil( results_count / float(limit_results)  ))
		
		return page_n_max



	### user functions for all handlers

	def get_user_from_db(self, user_email) :
		""" get user from db"""
		user 	   = self.application.coll_users.find_one({"email": user_email })
		return user 

	def get_current_user_auth_level(self):
		""" get user level """
		user_email 		= self.get_current_user_email()
		user			= self.get_user_from_db( user_email )
		try :
			user_auth_level = user.get("level_admin", "visitor" )
		except :
			user_auth_level = "visitor"	
		return user_auth_level

	def get_if_user_connected(self) :
		""" """
		is_user = self.get_current_user()
		if is_user != None :
			is_connected = "Yes"
		else : 
			is_connected = "No"
		return is_connected

	def get_current_user(self):
		""" return user_name"""
		return self.get_secure_cookie("user_name")
	
	def get_current_user_email(self):
		""" return user_name"""
		return self.get_secure_cookie("user_email")

	def get_current_user_id(self):
		
		user_email 	= self.get_current_user_email()
		# user 	   = self.application.coll_users.find_one({"email": user_email })
		user		= self.get_user_from_db( user_email )
		# return unicode(str(user["_id"]))
		return str(user["_id"])
	
	def add_user_to_db(self, user): 
		""" add a user config to db"""

		self.application.coll_users.insert_one( user )

	def set_current_user(self, user) :
		""" set cookie from user infos """

		if user : 
			# retrieve user data 
			user_name		= user["username"]
			user_password	= user["password"]
			user_email		= user["email"]

			# store info in cookie
			self.set_secure_cookie("user_name",  user_name )
			self.set_secure_cookie("user_email", user_email )
			self.set_secure_cookie("user_is_connected", "Yes" )

			# override self
			self.user_email = user_email

		else :
			# clear user if no user
			self.clear_current_user()

	def clear_current_user(self):
		""" clear cookies from client"""

		# if (self.get_argument("logout", None)):
		self.clear_cookie("user_name")
		self.clear_cookie("user_email")
		self.clear_cookie("user_is_connected")

	# TO CLEAN...
	def redirect_user_if_not_authorized(self, auth_level, site_section) :
		""" redirect user if he/she doen't have auth level for edition """

		redirect_user = False

		if auth_level not in ["all", "own"] : 
			
			app_log.warning("... redirect_user_if_not_authorized --- user %s don't have authorization level to enter %s", self.user_email, site_section ) 
			
			self.error_msg = self.add_error_message_to_slug( 
								error_string="you don't have the authorization level to access - {} - edition page".format(site_section),
								)
			redirect_to = REDIRECT_TO_IF_NOT_AUTHORIZED[ site_section ]

			self.redirect( redirect_to + self.error_msg)

			redirect_user = True 
			
			### TO CLEAN : still raising error / not clean .;;
			raise HTTPError(403)
			
		# return redirect_user
		return


	### DB functions for all handlers

	def choose_collection(self, coll_name=None ) :
		""" choose a db collection """

		if coll_name=="datamodel" :
			coll = self.application.coll_model
		if coll_name=="contributors" :
			coll = self.application.coll_spiders
		if coll_name=="data" :
			coll = self.application.coll_data
		if coll_name=="users" :
			coll = self.application.coll_users
		# else : 
		# 	self.set_status(404)

		app_log.info("... choose_collection / coll_name : %s", coll_name) 

		return coll

	def count_documents(self, coll_name="datamodel", query=None ) : 
		""" 
		simple count of documents in the db collection db_name
		passed "query" arg must be with the form : {"<field>" : "<value>"}
		ex : query={"field_class" : "custom"}
		"""

		print 
		app_log.info("... count_documents / coll_name : %s", coll_name)

		coll  = self.choose_collection ( coll_name=coll_name )
		count = coll.find(query).count()

		return count

	def count_all_documents(self, q_datamodel=None, q_contributors=None, q_data=None, q_users=None):
		"""count all collections' documents in db"""
		
		collections_to_count = {
			"datamodel"		: q_datamodel, 
			"contributors"	: q_contributors, 
			"data"			: q_data, 
			"users"			: q_users
		}

		app_log.info("... count_all_documents / collections_to_count : ")
		app_log.info("... %s ", collections_to_count )

		counts 	= { "count_{}".format(k) : self.count_documents(coll_name=k, query=v) for k,v in collections_to_count.iteritems() }
		
		print 

		return counts

	def count_docs_by_field(self, coll_name="data", field_name="spider_id") :
		"""count all documents in a collection and aggregate by a field"""

		coll = self.choose_collection(coll_name=coll_name)

		count_by_field = coll.aggregate( 	[{
											"$group" : 
												{ 
												"_id" : "${}".format(field_name), 
												"total_docs" : { "$sum" : 1 }
												} 
											}]
										)

		count_list = list(count_by_field)
		count_by_field_dict = { i["_id"] : i["total_docs"] for i in count_list }

		return count_by_field_dict

	def get_datamodel_fields(self, query=None) :
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

	def get_authorized_datamodel_fields(self, open_level, data_model_custom, data_model_core ):
		""" 
		retrieve a list of authorized fields given datamodel and open_level 
		for data query mainly
		"""

		allowed_open_levels 	= OPEN_LEVEL_DICT[open_level]
		allowed_custom_fields	= [ unicode(str(dm["_id"])) for dm in data_model_custom if dm["field_open"] in allowed_open_levels ]
		allowed_core_fields		= [ dm["field_name"] 		for dm in data_model_core 	if dm["field_open"] in allowed_open_levels ]
		
		allowed_fields 			= allowed_core_fields + allowed_custom_fields

		app_log.info("••• get_authorized_datamodel_fields / allowed_fields : %s", allowed_fields )

		return allowed_fields

	def filter_slug(self, slug, slug_class=None, query_from="app") : 
		""" filter args from slug """
		
		print
		app_log.info("... filter_slug / slug : \n %s ", pformat(slug) ) 

		# recreate query from slug
		raw_query = QueryFromSlug( slug, slug_class, query_from = query_from )	# from settings_corefields
		app_log.info("... filter_slug / raw_query.query : \n %s \n", pformat(raw_query.query) ) 

		return raw_query.query

	def build_first_term_query(self, query_obj, ignore_fields_list=[], keep_fields_list=[], data_model_custom_dict_names={}) :
		""" 
		build the query according to allowed fields ...
		"""

		print
		app_log.info("... build_first_term_query / query_obj : \n %s ", pformat(query_obj) )
		app_log.info("... build_first_term_query / keep_fields_list : \n %s ", pformat(keep_fields_list) )
		app_log.info("... build_first_term_query / data_model_custom_dict_names : \n %s \n", pformat(data_model_custom_dict_names) )

		query = {}

		### reroute query fields for first query arg
		# search by spider_id
		if "spider_id" in query_obj : 
			if "all" in query_obj["spider_id"] :
				pass
			else : 
				q_spider = { "spider_id" : q for q in query_obj["spider_id"] }
				query.update(q_spider)

		### search by content --> collection need to be indexed
		# cf : https://stackoverflow.com/questions/6790819/searching-for-value-of-any-field-in-mongodb-without-explicitly-naming-it
		if "search_for" in query_obj : 
			if query_obj["search_for"] != [] :
				
				# fields to search in is not specified
				if query_obj["search_in"] == [] : 
					# option choosen for now : in any field
					# cf : https://stackoverflow.com/questions/29020211/mongodb-cant-canonicalize-query-badvalue-too-many-text-expressions
					q_search_for = { "$text" : 
										{ "$search" : " ".join(query_obj["search_for"] ) } # doable because text fields are indexed at main.py
									}
					query.update(q_search_for)

				# field to search in is specified
				else :
					field_qs = []
					for f in query_obj["search_in"] :
						print f
						# check if f is custom or core
						if f in data_model_custom_dict_names : 
							f = unicode(data_model_custom_dict_names[f][u"_id"])
							print f, type(f)
						
						if f in keep_fields_list : 
							q_search_in = [ { f : {"$regex" : ".*{}.*".format(s) } } for s in query_obj["search_for"] ]  
							field_qs = field_qs + q_search_in 
					
					if field_qs != [] : 
						q_search_for = { "$or" : field_qs }
						query.update(q_search_for)

		return query

	def build_specific_fields(self, ignore_fields_list, keep_fields_list ) :
		""" projection of the query """

		# add ignore_fields / keep_fields criterias to query if any
		specific_fields = None
		if ignore_fields_list != [] or keep_fields_list != [] : 
			specific_fields = {}
			
			# add fields to ignore
			if ignore_fields_list != [] :
				ignore_fields = { f : 0 for f in ignore_fields_list }
				specific_fields.update( ignore_fields )
			
			# add fields to retrieve
			if keep_fields_list != [] :
				keep_fields = { f : 1 for f in keep_fields_list }
				specific_fields.update( keep_fields )

		return specific_fields

	# @run_on_executor # with raise gen.Return(result)
	def get_data_from_query(self, 
							query_obj, 
							coll_name, 
							query_from			= "app", # by default on "app", specify if comming from "api"
							
							ignore_fields_list	= [],
							keep_fields_list	= [],

							data_model_custom_dict_names = [],
							data_model_core_dict_names 	 = [],

							sort_by				= None, 
							) :
		""" get items from db """

		print
		app_log.info("... get_data_from_query / query_obj : \n %s \n", 			pformat(query_obj) )
		app_log.info("... get_data_from_query / keep_fields_list : \n %s \n", 	pformat(keep_fields_list) )
		app_log.info("... get_data_from_query / ignore_fields_list : \n %s \n", pformat(ignore_fields_list) )
		
		user_token		= query_obj["token"]

		# check if query wants all results
		all_results = False
		if "all_results" in query_obj : 
			all_results		= query_obj["all_results"]
		

		# TO DO : check if user has right to use specific query fields
		

		# TO DO 
		# retrieve all results at once 
		if all_results==True : 
			### TO DO 
			if user_token != None : # and 
				pass
			else : 
				all_results = False
				

		### DB OPERATIONS

		# choose collection
		app_log.info("... get_data_from_query / cursor :" )
		coll = self.choose_collection( coll_name=coll_name )

		# reroute query fields for first query arg (find)
		query = self.build_first_term_query(	query_obj, 
												ignore_fields_list			 = ignore_fields_list , 
												keep_fields_list			 = keep_fields_list , 
												data_model_custom_dict_names = data_model_custom_dict_names
											)
		app_log.info("... get_data_from_query / query : \n %s", pformat(query) )

		# add ignore_fields / keep_fields criterias to query if any (projection)
		specific_fields = self.build_specific_fields( ignore_fields_list, keep_fields_list )
		app_log.info("... get_data_from_query / specific_fields : %s ", specific_fields )

		# retrieve docs from db
		cursor 	= coll.find( query, specific_fields )

		# count results
		results_count	= cursor.count()

		# sort results
		if sort_by != None :
			cursor.sort( sort_by , pymongo.ASCENDING )

		# retrieve docs
		limit_results 	= query_obj["results_per_page"]

		# if query from "api" ignore pagination
		if query_from == "api" : 
			page_n_max   = None
			docs_from_db = list(cursor[ : limit_results ])
		# if query from "app" limit according to pagination
		else : 
			### compute max_pages, start index, stop index
			page_n 			= query_obj["page_n"]
			page_n_max 		= self.compute_count_and_page_n_max(results_count, limit_results)

			app_log.info("... get_data_from_query / results_cout : %s", results_count ) 
			app_log.info("... get_data_from_query / page_n_max   : %s ", page_n_max ) 
			app_log.info("... get_data_from_query / page_n       : %s ", page_n )

			### select items to retrieve from list and indices start and stop
			# all results case
			if all_results==True : 		
				docs_from_db = list(cursor)
			else : 
				# page queried is higher than page_n_max or inferior to 1
				if page_n > page_n_max or page_n < 1 :
					docs_from_db = []	
				# slice cursor : get documents from start index to stop index
				else : 
					results_i_start	= ( page_n-1 ) * limit_results 
					results_i_stop	= ( results_i_start + limit_results + 1 ) - 1
					app_log.info("... get_data_from_query / results_i_start : %s ", results_i_start )
					app_log.info("... get_data_from_query / results_i_stop  : %s ", results_i_stop )
					docs_from_db 	= list(cursor[ results_i_start : results_i_stop ])
			app_log.info("... get_data_from_query / docs_from_db : \n ....")
			# app_log.info("%s", pformat(docs_from_db[0]) )


		# flag if the cursor is empty
		is_data = False
		if docs_from_db != [] :
			is_data = True
		app_log.info("... get_data_from_query / is_data : %s \n ", is_data)

		return docs_from_db, is_data, page_n_max
		# raise gen.Return([ docs_from_db, is_data, page_n_max ] )
	
	
	### specific spider functions

	def update_spider_log(self, spider_id=None, spider_oid=None, log_to_update=None, value=None) :
		""" update log of a spider """

		app_log.info("... update_spider_log --- spider_id %s updating / log_to_update : %s", spider_id, log_to_update)

		# find the spider
		spider = self.application.coll_spiders.find_one( {"_id": spider_oid } )

		# update
		if spider != None : 
			self.application.coll_spiders.update_one( 
														{"_id"	: spider_oid }, 
														{"$set" : { "scraper_log.{}".format(log_to_update) : value } },
														upsert = True
													)
			app_log.info("... update_spider_log --- spider updated...")

		else : 
			app_log.error("... update_spider_log --- THERE IS NO spider_id %s", spider_id)
