
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
		self.spider_config = deepcopy(CONTRIBUTOR_CORE_FIELDS)
		
		### begin with no spidername
		spidername = ""

		### form exists 
		if form!=None : 
			# create a spidername and clean/escape it
			spidername = re.escape(form["name"][0])
			# del _id and _xsrf
			del form['_id']
			del form['_xsrf']
			# cleaning post dict
			form = { k : v[0] for k,v in form.iteritems() }
			form['notes'] = re.escape(form['notes'] )
			form['notes'] = form['notes'].split('\r\n')		

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
		if new_spider == True :
			self.spider_config["scraper_config"]["spidername"]	= spidername
			self.spider_config["scraper_log"]["added_by"] 		= user
			self.spider_config["scraper_log"]["modified_by"] 	= user

		print "\n*** SpiderConfig / finishing instance / contributor as self.spider_config : "
		# pprint.pprint (self.spider_config )
		print "\n***\n"


	def config_as_dict(self):
		return self.spider_config