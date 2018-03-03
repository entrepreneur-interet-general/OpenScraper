
"""
MAIN STRUCTURE FOR DB COLLECTIONS

MongoDB instantiated at Application level 

"""

### to instantiate datamodel core fields in mongoDB
DATAMODEL_FIELDS_TYPES = [
	"url", 
	"text", 
	"image", 
	"adress", 
	"date", 
	"tags", 
	"price"
]
DATAMODEL_CORE_FIELDS = [
	{"field_name" : "next_page", 		"field_type" : "text"},
	{"field_name" : "follow_xpath", 	"field_type" : "url"}, 
	{"field_name" : "link_data", 		"field_type" : "url"},
	{"field_name" : "link_src", 		"field_type" : "url"},
	{"field_name" : "added_by", 		"field_type" : "text"}, 
	{"field_name" : "item_created_at", 	"field_type" : "date"},
	
	{"field_name" : "testClass", "field_type" : "text"}
]
DATAMODEL_DEFAULT_CUSTOM_FIELDS = [
	{"field_name" : "author",	"field_type" : "text"},
	{"field_name" : "abstract", "field_type" : "text"},
	{"field_name" : "tags", 	"field_type" : "tags"},
	{"field_name" : "url", 		"field_type" : "url"},
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
		"follow_xpath" : None,
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
			"next_page",
			"parse_follow",
			"follow_xpath",
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