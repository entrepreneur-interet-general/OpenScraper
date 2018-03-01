
"""
MAIN STRUCTURE FOR DB COLLECTIONS

MongoDB instantiated at Application level 

"""

### to instantiate datamodel core fields in mongoDB
DATAMODEL_CORE_FIELDS = [
	"next_page",
	"link_data",
	"link_src",
	"item_created_at",
	"added_by", 

	"testClass"
]

### to instantiate contributor core fields in mongoDB
CONTRIBUTOR_CORE_FIELDS = {

	# custom infos 
	"infos" : {
		"name" : None , 	# real name contributor
		"page_url" : None ,
		"contact" : None,
		"notes" : None,
		"added_by" : None,
	},

	# scraper - custom for scraping basics
	 "scraper_config" : {
		"spidername" : None,
		"start_urls" : [],
		"parse_follow" : False,
		"page_needs_splash" : False,
	},

	# scraper - custom for scraping xpaths
	"scraper_config_xpaths" : {
		"next_page_xpath" : None,
	},

	# scraper - global settings	
	"scraper_settings" : {
		"LIMIT" : 100,
		"download_delay" : 0,
		"page_count" : 1,
	},

	# scraper stats	
	"stats" : {
		"error_array" : [],
		"item_count" : 0,
		"item_count_depth_1" : 0
	},

}

CONTRIBUTOR_EDIT_FIELDS = {

	### fields displayed in edit contributor page
	### "needed" = to be displayed
	### "optional" = optional (in drawer)

	# custom infos 
	"infos" : {
		"needed" : [
			"name", 
			"page_url",
			# "added_by",
		],
		"optional" : [
			"contact",
			"notes",
		]
	},

	# scraper - custom for scraping basics
	 "scraper_config" : {
		"needed" : [
			"spidername" ,
			"start_urls",
			# "next_page_xpath",
			"parse_follow",
		], 
		"optional": [
			"page_needs_splash",
		]
	 },

	# # scraper - custom for scraping xpaths
	# "scraper_config_xpaths" : {
	# 	"next_page_xpath" : None,
	# },

	# # scraper - global settings	
	# "scraper_settings" : {
	# 	"LIMIT" : 100,
	# 	"download_delay" : 0,
	# 	"page_count" : 1,
	# },

	# # scraper stats	
	# "stats" : {
	# 	"error_array" : [],
	# 	"item_count" : 0,
	# 	"item_count_depth_1" : 0
	# },
}

### to instantiate user core fields in mongoDB
USER_CORE_FIELDS = [
	"username",
	"email",
	"uuid",		#
	"password" 	# needs to be hashed
]