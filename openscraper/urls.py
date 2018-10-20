# -*- encoding: utf-8 -*-

from 	tornado.log import enable_pretty_logging, LogFormatter, access_log, app_log, gen_log


gen_log.info("--> importing .urls")

from controller 	import *
from spider_handler	import *
from api_handler	import *

### most routing functions are in controller.py
### for url mapping in Tornado cf : https://stackoverflow.com/questions/17166051/url-regex-mapping-in-tornado-web-server
### cf : https://code.tutsplus.com/tutorials/8-regular-expressions-you-should-know--net-6149
### cf : https://gist.github.com/c4urself/1028897
### cf : http://www.lexev.org/en/2014/set-url-for-tornado-handlers/
### cf : https://makandracards.com/theogfx/11605-python-+-tornado-variable-length-url-parameters
### cf : https://stackoverflow.com/questions/10726486/tornado-url-query-parameters
### cf : https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string

### cf : https://docs.python.org/2/library/re.html#regular-expression-syntax
### "/( ?P<your_arg>.*? )" - arg in url as kwarg
### "/( \w+ )" - string of letter
### "/( [0-9Xx\-]+ )" - string of numbers  numbers and dashes
### "/( .* )" - whatever comes

### "( [^/]+ )" - as slug
### if url is like "/api/?q=this&r=that" --> self.request.arguments gets : {'q': ['this'], 'r': ['that']} 

urls = [

	### index
	(r"/", 				WelcomeHandler),


	### login, register, logout
	# (r'/login/(?P<next>.*?)', 		LoginHandler),
	(r'/login/', 		LoginHandler),
	(r'/register/', 	RegisterHandler),
	(r'/logout/', 		LogoutHandler),
	# TO DO 
	(r'/preferences/', 	UserPreferences),

	### infos
	(r'/infos/who', 		WhoHandler),
	(r'/infos/tuto', 		TutoHandler),
	(r'/infos/api', 		APIdocHandler),

	### bulma tests : just for debugging and speeding UI front dev
	(r"/datamodel/form", FormHandler),
	(r"/test_bulma_ext", TestBulmaHandler),


	### datamodel : edit or create fields to structure what you gonna crawl
	(r"/datamodel/view", 		DataModelViewHandler),
	(r"/datamodel/edit", 		DataModelEditHandler),
	(r"/datamodel/add_field", 	DataModelAddFieldHandler),


	### contributors :the websites to crawl
	(r"/contributors?([^/]*)?", 			ContributorsHandler),
	
	(r"/contributor/add", 					ContributorEditHandler),
	(r"/contributor/edit/([\w\_\d]+)",		ContributorEditHandler), 
	
	(r"/contributor/reset_data", 			ContributorResetDataHandler), 
	(r"/contributor/delete", 				ContributorDeleteHandler), 
	

	### dataset routes
	# cf : https://stackoverflow.com/questions/10726486/tornado-url-query-parameters 
	(r"/dataset/view([^/]*)", 		DataScrapedHandler), 	### get optional(*) parameters in slug like : dataset/view?page=0&stuff=3
	# (r"/dataset/view/(\w+)",		DataScrapedViewOneHandler),


	### spider launchers / runners
	(r"/crawl?([^/]*)?", 			SpiderHandler), ### get spidername as input





	### API routes
	# (r"/api/.*", 					PageNotFoundHandler),
	(r"/api/data?([^/]*)?",			APIrestHandlerData),
	(r"/api/infos?([^/]*)?", 		APIrestHandlerInfos),
	(r"/api/stats?([^/]*)?", 		APIrestHandlerStats),
	# (r"/api/(?P<page_n>[0-9]+)", 	PageNotFoundHandler),
	# (r"/api/(?P<project>.*?)", 		PageNotFoundHandler),


	# TO DO ...
	(r"/(ajax)$", 	AjaxHandler),


	### error route : 404
	(r'.*', 						PageNotFoundHandler),

]