
import tornado.web, tornado.template

from scraper import run_test_spider 

### REQUEST HANDLERS

class MainHandler(tornado.web.RequestHandler):
	"""
	handler for index page
	"""
	def get(self):

		self.render(
			"index.html",
			page_title = "CIS | spider manager",
			header_text = "Welcome to CIS's spider manager!",
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

class TestSpiderHandler(tornado.web.RequestHandler) : 
	"""
	test a basic spider : launch the run from client side
	"""
	def get(self):
		run_test_spider()



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