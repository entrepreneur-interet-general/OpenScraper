
from controller import *

### all routing functions are in controller.py
### for url mapping in Tornado cf : https://stackoverflow.com/questions/17166051/url-regex-mapping-in-tornado-web-server
### cf : https://code.tutsplus.com/tutorials/8-regular-expressions-you-should-know--net-6149
### cf : https://gist.github.com/c4urself/1028897
### cf : http://www.lexev.org/en/2014/set-url-for-tornado-handlers/

### cf : https://docs.python.org/2/library/re.html#regular-expression-syntax
### "/( ?P<your_arg>.*? )" - arg in url as kwarg
### "/( \w+ )" - string of letter
### "/( [0-9Xx\-]+ )" - string of numbers  numbers and dashes
### "/( .* )" - whatever comes
### "( [^/]+ )"
### if url is like "/api/?q=this&r=that" --> self.request.arguments gets : {'q': ['pants'], 'r': ['tata']} 

urls = [

	### index, login, register, logout
	(r"/", 				WelcomeHandler),
	(r'/login', 		LoginHandler),
	(r'/register', 		RegisterHandler),
	(r'/logout', 		LogoutHandler),
	(r'/preferences/', 	UserPreferences),

	### forms : just for test
	(r"/datamodel/form", FormHandler),

	### datamodel : edit or create fields to structure what you gonna crawl
	(r"/datamodel/view", 		DataModelViewHandler),
	(r"/datamodel/edit", 		DataModelEditHandler),
	(r"/datamodel/add_field", 	DataModelAddFieldHandler),

	### contributors : websites to crawl
	(r"/contributors", 				ContributorsHandler),
	(r"/contributor/add", 			ContributorEditHandler),
	(r"/contributor/edit/([\w\_\d]+)",	ContributorEditHandler), 
	(r"/contributor/delete/([\w\_\d]+)", ContributorDeleteHandler), 

	### spider launchers
	# (r"/crawl/(\w+)", 			SpiderHandler), ### get spidername as input
	(r"/crawl/([\w\_\d]+)",			SpiderHandler), ### get spidername as input

	### dataset routes
	# cf : https://stackoverflow.com/questions/10726486/tornado-url-query-parameters 
	(r"/dataset/view([^/]*)", 		DataScrapedHandler), 	### get optional(*) parameters in slug like : dataset/view?page=0&stuff=3
	(r"/dataset/view/(\w+)",		DataScrapedViewOneHandler),
	
	### API routes
	(r"/api/.*", 					PageNotFoundHandler),
	(r"/api/([^/]*)",				PageNotFoundHandler),

	(r"/api/search?=(.*)", 			PageNotFoundHandler),
	(r"/api/(?P<page_n>[0-9]+)", 	PageNotFoundHandler),
	(r"/api/(?P<project>.*?)", 		PageNotFoundHandler),
	
	### error route : 404
	(r'.*', 						PageNotFoundHandler),

]