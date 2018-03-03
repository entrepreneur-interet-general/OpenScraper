
from controller import *

### all routing functions are in controller.py
urls = [

	### index, login, register, logout
	(r"/", WelcomeHandler),
	(r'/login', LoginHandler),
	(r'/register', RegisterHandler),
	(r'/logout', LogoutHandler),

	### forms : just for test
	(r"/datamodel/form", FormHandler),

	### datamodel : edit or create fields to structure what you gonna crawl
	(r"/datamodel/view", DataModelViewHandler),
	(r"/datamodel/edit", DataModelEditHandler),
	(r"/datamodel/add_field", DataModelAddFieldHandler),

	### contributors : websites to crawl
	(r"/contributors", ContributorsHandler),
	(r"/contributor/edit/(\w+)", ContributorEditHandler), # ([0-9Xx\-]+) # for regex numbers and dashes
	(r"/contributor/add", ContributorEditHandler),

	### spider launchers
	(r"/crawl/(\w+)", SpiderHandler), ### get spidername as input

	### data routes
	(r"/data", DataScrapedHandler),
	(r"/data/view/(\w+)", DataScrapedViewOneHandler),
	# (r"/data/api/search?=()", DataApiHandler),
	
	### error route : 404
	(r'.*', PageNotFoundHandler),

	
]