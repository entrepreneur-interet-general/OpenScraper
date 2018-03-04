
import pprint
import copy
from copy import deepcopy

from .settings_corefields import * 


class UserClass :
	"""
	a generic user class 
	can be sent to db as document once iniated with .__dict__()
	"""
	def __init__(self, **kwargs) :

		print "\n*** UserClass ..."

		print "\n*** UserClass / fields from USER_CORE_FIELDS ..."
		for user_field in USER_CORE_FIELDS :
			print user_field
			self.__dict__[user_field] = None

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

	def __init__(self, form=None, user="admin" ) :

		print "\n*** SpiderConfig ..."

		### clean form 
		if form!=None : 
			del form['_id']
			del form['_xsrf']

		### begin instance with empty CONTRIBUTOR_CORE_FIELDS
		self.spider_config = deepcopy(CONTRIBUTOR_CORE_FIELDS)
		
		### getting all the config args from spider_config (i.e. next_page_xpath, ...)
		print "*** SpiderConfig / form :"
		pprint.pprint(form)

		### update core contributor fields from spider_config_empty
		for key in ["infos", "scraper_config"] :
			print "\n*** SpiderConfig / self.spider_config / key : ", key
			for field in self.spider_config[key]:
				print field
				try :
					self.spider_config[key][field] = form[field]
				except :
					pass

		### update custom contributor fields from form
		if form!=None : 
			not_custom_fields = CONTRIBUTOR_CORE_FIELDS["scraper_config"].keys() +  CONTRIBUTOR_CORE_FIELDS["infos"].keys()
			for field_custom in form.keys() :
				if field_custom not in not_custom_fields :
					print field_custom
					if form!=None :  
						self.spider_config["scraper_config_xpaths"][field_custom] = form[field_custom]

		### add specifics in infos
		self.spider_config["infos"]["added_by"] = user

		print "\n*** SpiderConfig / finishing instance / self.spider_config : "
		pprint.pprint (self.spider_config )
		print "\n***\n"


	def config_as_dict(self):
		return self.spider_config