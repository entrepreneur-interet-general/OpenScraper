
import tornado.web, tornado.template


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

class BookEditHandler(tornado.web.RequestHandler):
    """
    contributor edit handler
    """
    def get(self, isbn=None):
		book = dict()
		if isbn:
			coll = self.application.db.books
			book = coll.find_one({"isbn": isbn})
		self.render("contributor_edit.html",
			page_title="Burt's Books",
			header_text="Edit book",
			book=book)

    def post(self, isbn=None):
		import time
		book_fields = ['isbn', 'title', 'subtitle', 'image', 'author',
			'date_released', 'description']
		coll = self.application.db.books
		book = dict()
		if isbn:
			book = coll.find_one({"isbn": isbn})
		for key in book_fields:
			book[key] = self.get_argument(key, None)

		if isbn:
			coll.save(book)
		else:
			book['date_added'] = int(time.time())
			coll.insert_one(book)
		self.redirect("/recommended/")


class RecommendedHandler(tornado.web.RequestHandler):
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
		
class BookModule(tornado.web.UIModule):
    """
    module for each contributor
    """
    def render(self, book):
		return self.render_string(
			"modules/mod_contributor.html", 
			book=book,
		)
	
    def css_files(self):
		return "css/recommended.css"
	
    def javascript_files(self):
		return "js/recommended.js"