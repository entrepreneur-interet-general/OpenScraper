# -*- encoding: utf-8 -*-

import 	pprint
from 	pprint import pprint, pformat

import 	copy
from 	copy import deepcopy
import 	re
import 	time
from 	datetime import datetime

### TO DO / IMPLEMENT
### for JWT in Python, cf : https://github.com/jpadilla/pyjwt
import 	jwt

from .settings_corefields 	import * 
from .settings_queries 		import * 
from .settings_cleaning		import *

from tornado.log import access_log, app_log, gen_log


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### CORE CLASSES : USERS - SPIDERS - QUERIES ################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class UserClass :
	"""
	a generic user class when a new user is registred
	can be sent to db as a document once iniated with .__dict__()
	"""
	def __init__(self, **kwargs) :

		print
		app_log.warning("== UserClass ... ")

		app_log.warning("== UserClass / fields from USER_CORE_FIELDS ... ")
		for user_field in USER_CORE_FIELDS :
			app_log.warning("== UserClass / user_field : %s", user_field)
			self.__dict__[user_field] = ""

		app_log.warning("== UserClass / fields from **kwargs ...")
		for k, v in kwargs.items():
			# print "{} : {}".format(k,v)
			app_log.warning("== UserClass / %s : %s ...", k, v)
			try :
				self.__dict__[k] = v
			except : 
				pass

		print 

	### TO DO : hash password
	def hash_password(self) : 
		pass


class SpiderConfig :
	"""
	a spider config object that can be created from the contributor form...
	this class uses CONTRIBUTOR_CORE_FIELDS as backbone...
	this config would be then stored in db as dict/json ...
	"""

	def __init__(self, 
		form		= None, 
		new_spider	= False, 
		user		= None ) :

		app_log.info("== SpiderConfig ... ")

		app_log.info("== SpiderConfig / new_spider ... ")


		### prevent adding spider if user is not connected
		if user != None : 

			self.timestamp = time.time()

			### begin instance with empty CONTRIBUTOR_CORE_FIELDS
			self.user 			= user
			self.spider_config 	= deepcopy(CONTRIBUTOR_CORE_FIELDS)
			
			### begin with no spidername
			spidername = ""

			### form exists --> clean it
			if form!=None : 			
				# del _id and _xsrf
				del form['_id']
				del form['_xsrf']

				# cleaning post dict
				form = { k : v[0] for k,v in form.iteritems() }
				# form['notes'] = re.escape(form['notes'] )

				# optional : create a spidername and clean/escape it
				spidername 			= re.escape(form["name"])
				spidername			= spidername.replace('\\', '')

				form['start_urls'] 	= form['start_urls'].replace(',', ' ')		
				form['start_urls'] 	= form['start_urls'].split(' ')
				form['start_urls']  = [ i for i in form['start_urls'] if i!="" ]
				
				form['notes'] 		= form['notes'].replace("\n", "")
				form['notes'] 		= form['notes'].replace("\r", "")
				
				# clean radio field values
				for radio_field in CONTRIBUTOR_EDIT_FIELDS_RADIO : 
					if radio_field in form.keys() : 
						if form[radio_field] == "true" : 
							form[radio_field] = True
						else :
							form[radio_field] = False
				
				# clean number field values
				for num_field in CONTRIBUTOR_EDIT_FIELDS_NUMBER :
					if num_field in form.keys() : 
						if num_field in CONTRIBUTOR_EDIT_FIELDS_FLOAT :
							form[num_field] = float(form[num_field])
						else :
							form[num_field] = int(form[num_field])
							

			### getting all the config args from spider_config (i.e. next_page_xpath, ...)
			# print "*** SpiderConfig / cleaned form :"
			# pprint.pprint(form)
			app_log.info("== SpiderConfig / cleaned form : \n %s", pformat(form) )

			### update core contributor fields from spider_config
			
			for key in CONTRIBUTOR_CUSTOMAZIBLE_FIELDS :
				# print "\n*** SpiderConfig / self.spider_config / key : ", key
				print
				app_log.info("== SpiderConfig / self.spider_config / key : %s ", key )
				for field in self.spider_config[key]:
					app_log.info("== SpiderConfig / self.spider_config / field : %s ", field )
					try :
						self.spider_config[key][field] = form[field]
					except :
						pass

			### update custom contributor fields from form
			if form!=None : 
				# print "\n*** SpiderConfig / form.keys() :"
				print
				app_log.info("== SpiderConfig / form.keys() :" )
				for field_custom in form.keys() :
					if field_custom not in NOT_CUSTOM_DATAMODEL_FIELDS :
						# print "field_custom : ", field_custom
						app_log.info("== SpiderConfig / field_custom : %s ", field_custom )
						self.spider_config["scraper_config_xpaths"][field_custom] = form[field_custom]

			### add specifics in infos / scraperconfig
			self.spider_config["scraper_config"]["spidername"]	= unicode(spidername)
			if new_spider == True :
				self.spider_config["scraper_log"]["added_by"] 		= user
				self.spider_config["scraper_log"]["modified_by"] 	= user
				self.spider_config["scraper_log"]["added_at"] 		= self.timestamp

			print 
			app_log.info("== SpiderConfig / finishing instance / contributor as self.spider_config : \n %s", pformat(self.spider_config) )
			# print "\n*** SpiderConfig / finishing instance / contributor as self.spider_config : "
			# pprint.pprint (self.spider_config )
			print "\n***\n"


	def full_config_as_dict(self):
		""" return the spider configuration as a dict (to store it in db for instance) """
		return self.spider_config


	def partial_config_as_dict(self, previous_config=None ) : 
		""" """
		print 
		app_log.info("== SpiderConfig.partial_config_as_dict / previous_config : %s ", previous_config )
		# print "\n*** SpiderConfig.partial_config_as_dict / previous_config : "
		# print previous_config

		all_custom_fields = CONTRIBUTOR_CUSTOMAZIBLE_FIELDS + ["scraper_config_xpaths"]
		partial_config = { k : v for k,v in self.spider_config.iteritems() if k in all_custom_fields }
		# print "\n*** SpiderConfig.partial_config_as_dict / partial_config : "
		# print partial_config
		
		# reset scraper_log
		partial_config["scraper_log"] = deepcopy(CONTRIBUTOR_CORE_FIELDS["scraper_log"])
		partial_config["scraper_log"]["modified_by"]	= self.user
		partial_config["scraper_log"]["modified_at"]	= self.timestamp
		partial_config["scraper_log"]["added_by"] 		= previous_config["scraper_log"]["added_by"]

		return partial_config


class QueryFromSlug : 
	"""
	slug cleaner to translate complete or incomplete slug into a clean mongodb query
	"""

	def __init__(self, slug, slug_class, query_from="app" ) : 

		print
		app_log.info("== QueryfromSlug ... ")

		self.slug 		= slug
		self.slug_class = slug_class

		self.default_query 		= {}
		self.default_uniques 	= []
		self.default_integers 	= []
		self.default_bool 		= []
		
		# choose default query depending on slug_class
		if self.slug_class 		== "data" : 
			self.default_query 		= QUERY_DATA_BY_DEFAULT
			self.default_uniques 	= QUERIES_DATA_ALLOWED_UNIQUE
			self.default_integers 	= QUERIES_DATA_ALLOWED_INTEGERS
			self.default_positives 	= QUERIES_DATA_ALLOWED_POSITIVES
			self.default_bool 		= QUERIES_DATA_ALLOWED_BOOLEAN
		elif self.slug_class 	== "contributors" : 
			self.default_query 		= QUERY_SPIDER_BY_DEFAULT
			self.default_uniques 	= QUERIES_SPIDER_ALLOWED_UNIQUE
			self.default_integers 	= QUERIES_SPIDER_ALLOWED_INTEGERS
			self.default_positives 	= QUERIES_SPIDER_ALLOWED_POSITIVES
			self.default_bool 		= QUERIES_SPIDER_ALLOWED_BOOLEAN
		elif self.slug_class 	== "crawl" : 
			self.default_query 		= QUERY_CRAWL_BY_DEFAULT
			self.default_uniques 	= QUERIES_CRAWL_ALLOWED_UNIQUE
			self.default_integers 	= QUERIES_CRAWL_ALLOWED_INTEGERS
			self.default_positives 	= QUERIES_CRAWL_ALLOWED_POSITIVES
			self.default_bool 		= QUERIES_CRAWL_ALLOWED_BOOLEAN

		# clean default_query if query is coming from api 
		if query_from == "api" :
			print QUERIES_ARGS_TO_IGNORE_IF_API
			self.default_query = { k : v for k,v in self.default_query.iteritems() if k not in QUERIES_ARGS_TO_IGNORE_IF_API }
			self.default_query["results_per_page"] = QUERIES_MAX_RESULTS_IF_API

		# copy chosen default query as backbone
		self.query 	= deepcopy(self.default_query)

		# populate default query with args from slug if a slug
		if slug != {} and self.slug_class in ["data", "contributors", "crawl"] :
			self.populate_query()
		

	def populate_query(self) : 
		""" populate default query """

		for q_field, q_arg in self.slug.iteritems() : 
			app_log.info( "=== QueryFromSlug.populate_query / q_field : %s ", q_field )

			# only get allowed query fields from slug so to ignore others
			if q_field in self.default_query.keys() :

				if q_field in self.default_uniques : 

					# select one unique value for this arg (not a list)
					self.query[q_field] = q_arg[0]

					# value should be an integer 
					if q_field in self.default_integers :
						try : 
							self.query[q_field] = int(self.query[q_field])
							
							# value should be positive, keep default value if not
							if q_field in self.default_positives :
								if self.query[q_field] < 0 :
									# deprecated : absolute value 
									# self.query[q_field] = abs(self.query[q_field]) # for absolute value
									# reset to zero
									self.query[q_field] = 0
						except : 
							self.query[q_field] = self.default_query[q_field]

					# value should be a boolean 
					elif q_field in self.default_bool :
						# if self.query[q_field] in ["yes", "YES", "true", "True", "TRUE", "1", "t", "T"] :
						if self.query[q_field] in SYNONYMS_TRUE :
							self.query[q_field] = True
						# elif self.query[q_field] in ["no", "NO", "false", "False", "FALSE", "0", "f", "F"] : 
						elif self.query[q_field] in SYNONYMS_FALSE : 
							self.query[q_field] = False
						else : 
							# keep original value if neither
							pass

				else : 
					# split query list by space (if + sign is notified)
					# self.query[q_field] = q_arg
					raw_q_list = []
					for q in q_arg :  	# for every list if q_arg is repeated
						q_ = q.split()	# split string content into list when args are separated by a space
						for i in q_ : 	# for every arg add it to raw_q_list
							raw_q_list.append(i)
					self.query[q_field] = raw_q_list


		# print "=== QueryFromSlug.populate_query / self.query : "
		# print self.query