
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




class SpiderHandler(BaseHandler) : 
	"""
	launch run_generic_spider from client side (and from url arg spider_id) as background task 
	"""
	# @gen.coroutine
	@print_separate(APP_DEBUG)
	@tornado.web.authenticated
	@onthread
	def get(self, slug=None ):
		
		print 
		app_log.info("SpiderHandler.get... ")

		# catch error message if any
		# self.catch_error_message()

		app_log.info("SpiderHandler.get / slug : %s", slug )

		slug_ = self.request.arguments
		app_log.info("SpiderHandler.get / slug_ : \n %s", pformat(slug_) )

		# filter slug
		query_contrib = self.filter_slug( slug_, slug_class="crawl" )
		app_log.info("SpiderHandler.get / query_contrib : \n %s ", pformat(query_contrib) )

		# get spider_id to crawl
		spider_id 	= query_contrib["spider_id"]
		spider_oid 	= ObjectId(spider_id)

		app_log.info("SpiderHandler.get / spider_id : %s", spider_id )
		print spider_oid, type(spider_oid)

		### retrieve spider config from its name in the db
		# spider_config = self.application.coll_spiders.find_one({"scraper_config.spidername": spidername})
		try : 
			spider_config = self.application.coll_spiders.find_one( {"_id": spider_oid } )
		except : 
			spider_config = None
		
		
		### set default runner if no spider_config
		if spider_config == None : 
			
			app_log.warning("SpiderHandler.get --- !!! spider_id -%s- not found : test spider with test_config", spider_id ) 
			
			self.error_msg = self.add_error_message_to_slug( 
								error_string="ERROR !!! there is no spider configuration with -%s- spider_id in the DB" %(str(spider_id)),
								args_to_delete=QUERY_CRAWL_BY_DEFAULT.keys()
								)

			# redirect client before starting spider
			self.redirect("/contributors" + self.error_msg )
			
		
		else : 

			# redirect client before starting spider
			self.redirect("/contributors"  )

			app_log.info("SpiderHandler.get --- spider_id     : %s ", spider_id )
			app_log.info("SpiderHandler.get --- spider_config : %s ", pformat(spider_config["infos"]) )


			# update spider log
			self.update_spider_log(spider_id=spider_id, spider_oid=spider_oid, log_to_update="is_running", 		  value=True)
			self.update_spider_log(spider_id=spider_id, spider_oid=spider_oid, log_to_update="is_data_available", value=False)


			### asynchronous run the corresponding spider
			app_log.info("SpiderHandler.get --- starting spider runner --- " )
			
			### getting data_model lists
			app_log.info("SpiderHandler.get --- creating data model list from fields in db ")
			data_model = list(self.application.coll_model.find({}))
			app_log.info("SpiderHandler.get --- data_model[:3] from db : \n %s \n...", pformat(data_model[:3]) )

			yield self.run_spider( 	
									datamodel 		= data_model,
									spider_id 		= spider_id,
									spider_oid 		= spider_oid, 
									spider_config	= spider_config, 
									current_user_id	= self.get_current_user_id()
							 ) 
			# self.finish()




	# @gen.coroutine	# with raise gen.Result(result)
	# @return_future	# with callback(result) / cf : http://www.maigfrga.ntweb.co/asynchronous-programming-tornado-framework/
	@print_separate(APP_DEBUG)
	@run_on_executor	# with raise gen.Return(result)
	def run_spider (	self, 
						datamodel,
						spider_id, 
						spider_oid,
						spider_config,
						current_user_id,
						# callback=None,
						countdown=3
					) :
		
		print 
		app_log.info("SpiderHandler.run_spider --- " )
		

		### for debugging purposes...
		app_log.info("SpiderHandler.run_spider / testing the non-blocking decorator with a time.sleep... " )
		time.sleep(1)
		# app_log.info("SpiderHandler.run_spider ---\n--- start spider %s in %s" %( str(spider_id), countdown ) ) 
		for i in range( countdown ):
			time.sleep(1)
			app_log.info("SpiderHandler.run_spider ---\n--- start spider %s in %s" %( str(spider_id), countdown-i ) ) 
		time.sleep(1)


		### run spider --- check masterspider.py --> function run_generic_spider()
		app_log.info("SpiderHandler.run_spider / now let it run... ")
		result = run_generic_spider( 
									user_id				= current_user_id,
									spider_id			= str(spider_id), 
									# spider_oid		= spider_oid,
									datamodel			= datamodel, 
									run_spider_config	= spider_config 
									)


		### TO DO : keep track of error and update status in spider configuration
		### update scraper_log.is_working
		# app_log.info("SpiderHandler.get --- spider is_working updating...")
		# self.application.coll_spiders.update_one( 
		# 										{"_id": ObjectId(spider_id) }, 
		# 										{"$set" : {"scraper_log.is_working" : True} }
		# 										)
		# app_log.info("SpiderHandler.get --- spider is_working updated...")
		self.update_spider_log(spider_id=spider_id, spider_oid=spider_oid, log_to_update="is_working", 		  value=True)
		self.update_spider_log(spider_id=spider_id, spider_oid=spider_oid, log_to_update="is_running", 		  value=False)
		self.update_spider_log(spider_id=spider_id, spider_oid=spider_oid, log_to_update="is_data_available", value=True)

		### raise result to tell gen is ended
		raise gen.Return(result)
		# yield gen.Return(result)
		# callback(result)
