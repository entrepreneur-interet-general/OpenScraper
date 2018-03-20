
from 	base_handler import *
from 	base_utils	import *

# from 	tornado.log import access_log, app_log, gen_log # already imported from base_handler

### OpenScraper generic scraper
from scraper import run_generic_spider 


########################
### RUN SPIDER handlers as background tasks

# threading for background tasks (spiders mainly)
# cf : https://stackoverflow.com/questions/22082165/running-an-async-background-task-in-tornado/25304704
# cf : https://gist.github.com/marksilvis/ea1142680db66e2bb9b2a29e57306d76
# cf : https://stackoverflow.com/questions/22082165/running-an-async-background-task-in-tornado
# cf : https://gist.github.com/mivade/421c427db75c8c5fa1d1
# cf : http://www.tornadoweb.org/en/stable/faq.html#my-code-is-asynchronous-but-it-s-not-running-in-parallel-in-two-browser-tabs
# cf : http://www.tornadoweb.org/en/stable/guide/queues.html
# cf : https://emptysqua.re/blog/refactoring-tornado-coroutines/

""" prefilled fields for early tests

	test_data_model = [
		

		# item source and
		"link_data", 
		"link_src", 
		"link_to",

		# item contents
		"title", 
		"img", 
		"abstract", 
		"tags", # keywords
		"raw_date", 

		# item 
		"area",
		"adress",

		# item metadata 
		"author",
		"date_data",
		"item_created_at",

		### for debugging purposes
		"testClass"
	]

	test_spider_config = {

		### custom mandatory fields
		"name"  : "TEST", 
		# "label" : "test_spider_config",
		"page_url" : "http://quote.toscrape.com", # base url (ex : "https://www.mysite.org")
		"start_urls" : [ # List of URLs that will be crawled by the parse method
			'http://quotes.toscrape.com/'
		],

		### custom notes
		"notes" : u"test configuration for debugging / developping purposes...",

		### settings and logging fields
		"error_array" : [],
		"item_count": 0, # will be incremented each time a new item is created
		"item_count_depth_1" : 0,# will be incremented each time an item is completed in detailed page
		"LIMIT" : 10, # The number of pages where the spider will stop
		"page_count" : 1, # The number of pages already scraped
		"download_delay" : 0, # The delay in seconds between each request. some website will block too many requests


		### custom boolean on whether the page contains complete items or need to follow links
		"parse_follow" : False, 

		### custom info if website needs AJAX requests...
		"page_needs_splash" : False,

		### custom xpaths for next_page, filled by user
		"next_page_xpath" :'//li[@class="next"]/a/@href', 
		# "action_xpath" : "",  

		### custom xpaths for item, filled by user
		"abstract_xpath" : './span[@class="text"]/text()',
		"author_xpath" : './/small[@class="author"]/text()',
		"tags_xpath" : './/div[@class="tags"]/a[@class="tag"]/text()',
		"rawdate_xpath" : ""
	} 

	avise_spider_config = {
		
		### mandatory fields
		"name" : "avise",
		"label" : "Avise",

		"page_url" : "http://www.avise.org",
		"start_urls" : ['http://www.avise.org/portraits', ],

		### notes
		"notes" : u"test configuration for debugging / developping purposes...",

		### settings and logging fields
		"error_array" : [],
		"item_count": 0, # will be incremented each time a new item is created
		"item_count_depth_1" : 0,# will be incremented each time an item is completed in detailed page
		"LIMIT" : 1, # The number of pages where the spider will stop
		"page_count" : 1, # The number of pages already scraped
		"download_delay" : 0, # The delay in seconds between each request. some website will block too many requests

		"list_xpath_selector" : '//div[@class:"view-content"]//div[@onclick]',
		"next_page_xpath" : '//li[@class:"pager-next"]/a/@href',

		# 
		"img_xpath" : './/image/@*[name():"xlink:href"]',
		"link_xpath" : './/h2/a/@href',
		"abstract_xpath" : './/div[@class:"field-item even"]/text()',
		"title_xpath" : './/h2/a/text()',

		# In action page
		"date_xpath" : 	'//div[@class:"field field--name-field-created-year field--type-text field--label-inline ' \
						'clearfix"]//div[@class:"field-item even"]/text()',
		"area_xpath" : 	'//div[@class:"addressfield-container-inline locality-block country-FR' \
						'"]/span/text()',
		"key_words_xpath" : '//div[@class:"field field--name-field-portrait-domain ' \
						'field--type-text field--label-inline clearfix"]' \
						'//div[@class:"field-item even"]//text()',
		"contact_xpath" : '//div[@id:"node-portrait-full-group-portrait-coordonnees"]//text()',
		"video_xpath" : "",
		"state_xpath" : "",
		"project_holder_xpath" : '//div[@id:"node-portrait-full-group-portrait-coordonnees"]' \
								'//div[@class:"name-block"]/text()',
		"partner_xpath" : "",
		"economic_xpath" : "",
	}
"""

class SpiderHandler(BaseHandler) : 
	"""
	launch run_generic_spider from client side (and from url arg spider_id) as background task 
	"""
	# @gen.coroutine
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@onthread
	def get(self, spider_id = None ):
		
		print 
		app_log.info("SpiderHandler.get... ")

		# catch error message if any
		self.catch_error_message()

		# count all docs
		# counts = self.count_all_documents() 

		app_log.info("SpiderHandler.get / spider_id : %s", spider_id )
		# print spider_id 

		### retrieve spider config from its name in the db
		# spider_config = self.application.coll_spiders.find_one({"scraper_config.spidername": spidername})
		try : 
			spider_config = self.application.coll_spiders.find_one( {"_id": ObjectId(spider_id) } )
		except : 
			spider_config = None
		
		# redirect client before starting spider
		self.redirect("/contributors")
		
		### set default runner if no spider_config
		if spider_config == None : 
			
			app_log.warning("SpiderHandler.get --- !!! spider_id -%s- not found : test spider with test_config", spider_id ) 
			
			error_slug = self.add_error_message_to_slug( "ERROR !!! there is no ''%s'' spider_id configuration in the DB ..." %(str(spider_id)) )

			### TO DO : debug this error : "Cannot redirect after headers have been written"
			self.redirect("/" + error_slug )			
			# self.render(
			# 	"index.html",
			# 	page_title 			= app_main_texts["main_title"],
			# 	serv_msg 			= "ERROR !!! there is no ''%s'' spider configuration in the DB ..." %(spider_id),
			# 	user 				= self.current_user,
			# 	counts 				= counts,
			# 	error_msg			= self.error_msg,
			# 	is_user_connected 	= self.is_user_connected
			# )
		
		else : 
			app_log.info("SpiderHandler.get --- spider_id     : ", spider_id )
			app_log.info("SpiderHandler.get --- spider_config :", pformat(spider_config) )
			# pprint.pprint(spider_config)

			app_log.info("SpiderHandler.get --- starting spider runner --- " )
			### TO DO : CHECK IF REALLY WORKING : asynchronous run the corresponding spider
			# self.run_generic_spider( run_spider_config = spider_config ) # synchronous
			
			### getting data_model lists
			app_log.info("SpiderHandler.get --- creating data model list from fields in db ")
			# data_model 			= self.application.coll_model.distinct("field_name")
			data_model 			= list(self.application.coll_model.find({}))
			app_log.info("SpiderHandler.get --- data_model from db : \n %s ", pformat(data_model) )
			# pprint.pprint(data_model)

			yield self.run_spider( 	
									datamodel 		= data_model,
									spider_id 		= spider_id, 
									spider_config	= spider_config, 
									current_user_id	= self.get_current_user_id()
							 ) 
			# self.finish()

			# self.redirect("/contributors")

		### TO DO : redirect to a page showing crawling status / results
		# self.redirect("/contributors")
		
		# self.render(
		# 	"index.html",
		# 	page_title 	= app_main_texts["main_title"],
		# 	serv_msg 	= "crawling of -%s- finished ..." %(spider_id),
		# 	user 		= self.current_user,
		# 	counts 		= counts
		# )





	# @gen.coroutine	# with raise gen.Result(result)
	# @return_future	# with callback(result) / cf : http://www.maigfrga.ntweb.co/asynchronous-programming-tornado-framework/
	@print_separate(APP_DEBUG)
	@run_on_executor	# with raise gen.Return(result)
	def run_spider (	self, 
						datamodel,
						spider_id, 
						spider_config,
						current_user_id,
						callback=None,
						countdown=3
					) :
		
		print 
		app_log.info("SpiderHandler.run_spider --- " )
		
		app_log.info("SpiderHandler.run_spider / testing the non-blocking decorator with a time.sleep... " )
		app_log.info("SpiderHandler.run_spider ---\n--- start spider %s in %s" %( str(spider_id), countdown ) ) 
		for i in range( countdown ):
			time.sleep(1)
			app_log.info("SpiderHandler.run_spider ---\n--- start spider %s in %s" %( str(spider_id), countdown-i ) ) 
		time.sleep(1)

		### run spider --- check masterspider.py --> function run_generic_spider()
		app_log.info("SpiderHandler.run_spider / now let it run... ")
		result = run_generic_spider( 
									user_id				= current_user_id,
									spider_id			= str(spider_id), 
									datamodel			= datamodel, 
									run_spider_config	= spider_config 
									)



		### TO DO : keep track of error and update status in spider configuration
		### update scraper_log.is_working
		app_log.info("SpiderHandler.get --- spider updating...")
		self.application.coll_spiders.update_one( 
												{"_id": ObjectId(spider_id) }, 
												{"$set" : {"scraper_log.is_working" : True} }
												)
		app_log.info("SpiderHandler.get --- spider updated...")
		
		raise gen.Return(result)
		# yield gen.Return(result)
		# callback(result)
