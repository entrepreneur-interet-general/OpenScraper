
import 	pprint
import 	copy
from 	copy import deepcopy
import 	re

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

class SpiderConfig :
	"""
	a spider config object that can be created from form...
	this class uses CONTRIBUTOR_CORE_FIELDS as base...
	this config could be then stored in db...
	"""

	def __init__(self, 
		form		= None, 
		new_spider	= False, 
		user		= "admin" ) :

		print "\n*** SpiderConfig ... new_spider : ", new_spider

		### begin instance with empty CONTRIBUTOR_CORE_FIELDS
		self.user 			= user
		self.spider_config 	= deepcopy(CONTRIBUTOR_CORE_FIELDS)
		
		### begin with no spidername
		spidername = ""

		### form exists 
		if form!=None : 
			# create a spidername and clean/escape it
			# del _id and _xsrf
			del form['_id']
			del form['_xsrf']
			# cleaning post dict
			form = { k : v[0] for k,v in form.iteritems() }
			# form['notes'] = re.escape(form['notes'] )
			spidername 			= re.escape(form["name"])
			spidername			= spidername.replace('\\', '')

			form['start_urls'] 	= form['start_urls'].replace(',', ' ')		
			form['start_urls'] 	= form['start_urls'].split(' ')
			form['start_urls']  = [ i for i in form['start_urls'] if i!="" ]
			
			form['notes'] 		= form['notes'].replace("\n", "")
			form['notes'] 		= form['notes'].replace("\r", "")

		### getting all the config args from spider_config (i.e. next_page_xpath, ...)
		print "*** SpiderConfig / form :"
		pprint.pprint(form)

		### update core contributor fields from spider_config
		for key in ["infos", "scraper_config"] :
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
					if form!=None :  
						self.spider_config["scraper_config_xpaths"][field_custom] = form[field_custom]

		### add specifics in infos / scraperconfig
		self.spider_config["scraper_config"]["spidername"]	= unicode(spidername)
		if new_spider == True :
			self.spider_config["scraper_log"]["added_by"] 		= user
			self.spider_config["scraper_log"]["modified_by"] 	= user

		print "\n*** SpiderConfig / finishing instance / contributor as self.spider_config : "
		# pprint.pprint (self.spider_config )
		print "\n***\n"


	def full_config_as_dict(self):
		return self.spider_config

	def partial_config_as_dict(self, previous_config=None ) : 

		print previous_config
		partial_config = { k : v for k,v in self.spider_config.iteritems() if k in ["infos", "scraper_config", "scraper_config_xpaths"]}
		# reset scraper log
		partial_config["scraper_log"] = deepcopy(CONTRIBUTOR_CORE_FIELDS["scraper_log"])
		partial_config["scraper_log"]["modified_by"]	= self.user 
		partial_config["scraper_log"]["added_by"] 		= previous_config["scraper_log"]["added_by"]

		return partial_config