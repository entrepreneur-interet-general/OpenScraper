
from controller import *
# from admin import AdminHandler


### all routing functions are in controller.py
urls = [
	# (r"/", MainHandler),
	# (r"/test", TestHandler),

	### index
	(r"/", WelcomeHandler),
	(r'/login', LoginHandler),
	(r'/logout', LogoutHandler),

	### lists and edits
	(r"/contributors/", ContributorsHandler),
	(r"/edit/([0-9Xx\-]+)", ContributorEditHandler),
	(r"/add", ContributorEditHandler),

	### spider launchers
	(r"/crawl/(\w+)", SpiderHandler), ### get spidername as input


	# (r"/admin", AdminHandler),    
]