# -*- encoding: utf-8 -*-

import 	json
from bson import json_util, ObjectId

from 	base_handler import *
from 	base_utils	import *



### TO DO 


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### API handlers as background tasks ########################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

class APIrestHandler(BaseHandler): 
	"""
	list all contributors from db.contributors
	"""
	@print_separate(APP_DEBUG)
	# @tornado.web.authenticated
	# @check_user_permissions
	# @tornado.web.asynchronous
	@gen.coroutine
	def get(self, slug=None):

		app_log.info("APIrestHandler.get ...\n")

		self.site_section = "api"

		# get current page 
		current_page = self.get_current_uri_without_error_slug()
		app_log.info("APIrestHandler.get / current_page : %s", current_page )

		
		app_log.info("APIrestHandler.get / slug : %s", slug )

		slug_ = self.request.arguments
		app_log.info("APIrestHandler.get / slug_ : \n %s", pformat(slug_) )

		# filter slug
		query_contrib = self.filter_slug( slug_, slug_class="data" )
		app_log.info("APIrestHandler.get / query_contrib : \n %s ", pformat(query_contrib) )

		# get data 
		data, is_data, page_n_max = self.get_data_from_query( query_contrib, coll_name="data" )
		app_log.info("APIrestHandler.get / contributors[0] : \n %s " , pformat(data[0]) )
		print '.....\n'

		### operations if there is data
		if is_data : 
			
			app_log.info("APIrestHandler.get / is_data : %s ", is_data ) 
			
			self.write(json.dumps(data, default=json_util.default)) 