
import tornado.web, tornado.template
from tornado import gen

### import app settings / infos 
from config.app_infos import app_infos, app_main_texts
from config.settings_example import MONGODB_COLL_CONTRIBUTORS, MONGODB_COLL_DATAMODEL, MONGODB_COLL_DATASCRAPPED

### OpenScraper generic scraper
from scraper import run_generic_spider 


### REQUEST HANDLERS ###
"""
Tornado supports any valid HTTP method (GET,POST,PUT,DELETE,HEAD,OPTIONS)
"""

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
 

# class ContributorEditHandler(tornado.web.RequestHandler):
class ContributorEditHandler(BaseHandler):
	"""
	contributor edit handler
	"""
	def get(self, isbn=None):
		contributor = dict()
		if isbn:
			coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] # .books
			contributor = coll.find_one({"isbn": isbn})

		self.render("contributor_edit.html",
			page_title="CIS contributors",
			header_text="Edit contributor",
			contributor=contributor)

	def post(self, isbn=None):
		import time
		book_fields = [	'isbn', 'title', 'subtitle', 'image', 'author',
						'date_released', 'description']
		coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] # .books
		contributor = dict()
		if isbn:
			contributor = coll.find_one({"isbn": isbn})
		for key in book_fields:
			contributor[key] = self.get_argument(key, None)

		if isbn:
			coll.save(contributor)
		else:
			contributor['date_added'] = int(time.time())
			coll.insert_one(contributor)
		self.redirect("/recommended/")

# class ContributorsHandler(tornado.web.RequestHandler):
class ContributorsHandler(BaseHandler):
	"""
	list all contributors
	"""
	def get(self):
		coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] #db.contributors
		contributors = coll.find()
		self.render(
			"list_contributors.html",
			page_title = "List of contributors to CIS",
			header_text = "...",
			contributors = contributors
		)




test_spider_config = {
	"name"  : "TEST", 
	"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],

	"xpath_title" : "...",
	"xpath_abstract" : "...",
	"xpath_image" : "...",
} 


# class SpiderHandler(tornado.web.RequestHandler) : 
class SpiderHandler(BaseHandler) : 
	"""
	test a basic spider : launch the run from client side
	"""
	@tornado.web.authenticated
	@gen.coroutine
	def get(self, spidername = None ):
		
		print "\nSpiderHandler.get... "

		### retrieve spider config from its name in the db
		coll = self.application.db[ MONGODB_COLL_CONTRIBUTORS ] #.contributors
		spider_config = coll.find_one({"name": spidername})
		
		### redirect / set default runner if no spider_config
		if spider_config == None : 
			print "SpiderHandler.get --- !!! Spidername not found : test spider with test_config"
			# test_config = {
			# 		"name"  : "quote", 
			# 		"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],
			# 	 } 
			
			# (this will come from DB later)
			spider_config = test_spider_config
		
		print "SpiderHandler.get --- spidername : ", spidername
		print "SpiderHandler.get --- spider_config :", spider_config

		print "SpiderHandler.get --- starting spider runner --- "
		### TO CHECK IF REALLY WORKING : asynchronous run the corresponding spider
		# run_generic_spider( run_spider_config = spider_config ) # synchronous
		yield self.run_spider( spidername, spider_config=spider_config ) # asynchronous

		### TO DO : redirect to a page showing crawling status / results
		# self.redirect("/contributors/%s")
		self.render(
			"index.html",
			page_title = app_main_texts["main_title"],
			header_text = "crawling of -%s- launched ..." %(spidername),
			user = self.current_user
		)

	@gen.coroutine
	def run_spider (self, spidername, spider_config) :
		print "\nSpiderHandler.run_spider --- "
		result = run_generic_spider( spidername, run_spider_config = spider_config )
		raise gen.Return(result)



### TORNADO MODULES

class ContributorModule(tornado.web.UIModule):
	"""
	module for each contributor
	"""
	def render(self, contributor):
		return self.render_string(
			"modules/mod_contributor.html", 
			book=contributor,
		)
	
	def css_files(self):
		return "css/recommended.css"
	
	def javascript_files(self):
		return "js/recommended.js"