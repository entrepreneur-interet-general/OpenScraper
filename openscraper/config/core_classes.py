# -*- encoding: utf-8 -*-

import 	pprint
import 	copy
from 	copy import deepcopy
import 	re
import 	time
from 	datetime import datetime

### for JWT in Python, cf : https://github.com/jpadilla/pyjwt
import 	jwt

from .settings_corefields import * 


class UserClass :
	"""
	a generic user class 
	can be sent to db as a document once iniated with .__dict__()
	"""
	def __init__(self, **kwargs) :

		print "\n*** UserClass ..."

		print "\n*** UserClass / fields from USER_CORE_FIELDS ..."
		for user_field in USER_CORE_FIELDS :
			print user_field
			self.__dict__[user_field] = ""

		print "\n*** UserClass / fields from **kwargs ..."
		for k, v in kwargs.items():
			print "{} : {}".format(k,v)
			try :
				self.__dict__[k] = v
			except : 
				pass

	### TO DO : hash password
	def hash_password(self) : 
		pass

class SpiderConfig :
	"""
	a spider config object that can be created from form...
	this class uses CONTRIBUTOR_CORE_FIELDS as base...
	this config would be then stored in db...
	"""

	def __init__(self, 
		form		= None, 
		new_spider	= False, 
		user		= "admin" ) :

		print "\n*** SpiderConfig ... new_spider : ", new_spider

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
		print "*** SpiderConfig / cleaned form :"
		pprint.pprint(form)

		### update core contributor fields from spider_config
		
		# for key in ["infos", "scraper_config", "scraper_settings"] :
		for key in CONTRIBUTOR_CUSTOMAZIBLE_FIELDS :
			print "\n*** SpiderConfig / self.spider_config / key : ", key
			for field in self.spider_config[key]:
				print "field : ", field
				try :
					self.spider_config[key][field] = form[field]
				except :
					pass

		### update custom contributor fields from form
		if form!=None : 
			print "\n*** SpiderConfig / form.keys() :"
			for field_custom in form.keys() :
				if field_custom not in NOT_CUSTOM_DATAMODEL_FIELDS :
					print "field_custom : ", field_custom
					self.spider_config["scraper_config_xpaths"][field_custom] = form[field_custom]

		### add specifics in infos / scraperconfig
		self.spider_config["scraper_config"]["spidername"]	= unicode(spidername)
		if new_spider == True :
			self.spider_config["scraper_log"]["added_by"] 		= user
			self.spider_config["scraper_log"]["modified_by"] 	= user
			self.spider_config["scraper_log"]["added_at"] 		= self.timestamp

		print "\n*** SpiderConfig / finishing instance / contributor as self.spider_config : "
		# pprint.pprint (self.spider_config )
		print "\n***\n"


	def full_config_as_dict(self):
		return self.spider_config

	def partial_config_as_dict(self, previous_config=None ) : 

		print "\n*** SpiderConfig.partial_config_as_dict / previous_config : "
		print previous_config

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