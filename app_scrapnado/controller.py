
import tornado.web, tornado.template

from app_infos import app_infos, app_main_texts


from scraper import run_generic_spider 

### REQUEST HANDLERS

class MainHandler(tornado.web.RequestHandler):
	"""
	handler for index page
	"""
	def get(self):

		self.render(
			"index.html",
			page_title  = app_titles["main_title"],
			header_text = app_titles["main_header"],
		)

class ContributorEditHandler(tornado.web.RequestHandler):
	"""
	contributor edit handler
	"""
	def get(self, isbn=None):
		contributor = dict()
		if isbn:
			coll = self.application.db.books
			contributor = coll.find_one({"isbn": isbn})
		self.render("contributor_edit.html",
			page_title="CIS contributors",
			header_text="Edit contributor",
			book=contributor)

	def post(self, isbn=None):
		import time
		book_fields = ['isbn', 'title', 'subtitle', 'image', 'author',
			'date_released', 'description']
		coll = self.application.db.books
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

class ContributorsHandler(tornado.web.RequestHandler):
	"""
	list all contributors
	"""
	def get(self):
		coll = self.application.db.books
		contributors = coll.find()
		self.render(
			"recommended.html",
			page_title = "List of contributors to CIS",
			header_text = "...",
			books = contributors
		)

class SpiderHandler(tornado.web.RequestHandler) : 
	"""
	test a basic spider : launch the run from client side
	"""
	def get(self, spidername = "testspider" ):
		
		### retrieve spider config from its name in the db
		try : 
			coll = self.application.db.books
			spider_config = coll.find_one({"spider": isbn})
		except : 
			test_config = {
					"name"  : "quote", 
					"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],
				 } 
			spider_config = basic_config
		
		### run the corresponding spider
		run_generic_spider( run_spider_config = spider_config )

		### redirect to a page 
		self.render(
			"index.html",
			page_title = app_main_texts["main_title"],
			header_text = "crawling of -%s- finished..." %(spidername),
		)



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