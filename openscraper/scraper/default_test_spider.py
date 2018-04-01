# -*- encoding: utf-8 -*-

from pprint import pprint
from config.core_classes import SpiderConfig



def create_default_spider( coll_model, coll_spiders ):
	"""
	add a default test spider to coll
	"""

	# find existing custom fields
	custom_field_author 	= coll_model.find_one( {"field_class" : "custom", "field_name" : "author"})
	custom_field_abstract 	= coll_model.find_one( {"field_class" : "custom", "field_name" : "abstract"}  )
	custom_field_tags 		= coll_model.find_one( {"field_class" : "custom", "field_name" : "tags"} )
	
	pprint (custom_field_tags)

	# recreate spider form
	spider_config_form = {

		"_id" 	: "deprecated",
		"_xsrf" : "deprecated",

		# "infos" : {
		"notes" 	: "test configuration for debugging / developping purposes...",
		"contact" 	: "",
		"name" 		: "test quote",
		"page_url" 	: "http://quotes.toscrape.com",
		# },

		# "scraper_config" : {
		"next_page" 		: '//li[@class="next"]/a/@href',
		"start_urls" 		: [ 
			"http://quotes.toscrape.com/"
		],
		"item_xpath" 		: '//div[@class="quote"]',
		"page_needs_splash" : "false",
		"parse_follow" 		: "false",
		# "spidername" : "test quote",
		# "item_list_xpath" : "",
		# "follow_xpath" : "",
		# },
		
		# "scraper_config_xpaths" : {
		str(custom_field_tags["_id"]) 		: './/div[@class="tags"]/a[@class="tag"]/text()',
		str(custom_field_author["_id"]) 	: './/small[@class="author"]/text()',
		str(custom_field_abstract["_id"])	: './span[@class="text"]/text()',
		# }

	}
	
	# create contributor object
	contributor_object = SpiderConfig( 
			form 		= spider_config_form,
			new_spider 	= True,
			user		= "admin"
	)
	contributor = contributor_object.full_config_as_dict()
	pprint(contributor)

	# insert new spider to db
	coll_spiders.insert_one(contributor)