
from controller import *

### all routing functions are in controller.py
urls = [

	### index
	(r"/", WelcomeHandler),
	(r'/login', LoginHandler),
	(r'/logout', LogoutHandler),

	### set DB structure 
	(r"/datamodel/view", DataModelHandler),
	(r"/datamodel/edit", DataModelHandler),

	### lists and edits
	(r"/contributors", ContributorsHandler),
	(r"/contributor/edit/([0-9Xx\-]+)", ContributorEditHandler),
	# (r"/contributor/edit/(\w+)", ContributorEditHandler),
	(r"/contributor/add", ContributorEditHandler),

	### spider launchers
	(r"/crawl/(\w+)", SpiderHandler), ### get spidername as input

	### all data routes
	# (r"/data", DataHandler),
	# (r"/data/api/search?=()", DataApiHandler),
	
]