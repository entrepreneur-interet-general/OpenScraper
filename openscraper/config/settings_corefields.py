# -*- encoding: utf-8 -*-

"""
MAIN STRUCTURE FOR DB COLLECTIONS

MongoDB instanciated at Application level 

"""
import pprint



### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### USERS ###################################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

USER_AUTH_LEVELS = {
	"admin"   	: {	"datamodel" : "all", 
					"spiders" 	: "all", 	
					"data" 		: "all"  
					}, 	# can modify and view everything
	"staff"		: {	"datamodel" : "own", 
					"spiders" 	: "own", 	
					"data" 		: "collective"  
					},		# can modify its own fields in datamodel, can modify its own spiders
	"user"	  	: {	"datamodel" : "none", 
					"spiders" 	: "own", 	
					"data" 		: "commons"  
					},		# cannot modify fields in datamodel, can modify its own spiders
	"visitor" 	: {	"datamodel" : "none", 
					"spiders" 	: "none", 	
					"data" 		: "opendata" 
					},		# cannot modify anything
}
### to initiate user core fields in mongoDB
USER_CORE_FIELDS = [
	
	"username",
	"email",
	"password", 					# TO DO : needs to be hashed at register

	"added_at",
	"modified_at",

	"level_admin",					# TO DO 
	"spiders_authorized_to_modify", # TO DO 

	"organization",					# TO DO 
	"organization_url",				# TO DO 
	"picture",						# TO DO 
	"logo",							# TO DO 

	"preferences", 					# TO DO 
	"uses", 						# TO DO 

	"public_key"					# TO DO
]


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### DATAMODEL ################################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

### to initiate datamodel core fields in mongoDB
# field_type options in form and db
DATAMODEL_FIELDS_TYPES = [
	"url", 
	"text", 
	"email", 
	"image", 
	"adress", 
	"date", 
	"tags", 
	"price",
	"list"
]

# field_keep options in form only
DATAMODEL_FIELD_KEEP_VARS = [
	"keep", "not visible", "delete", 
]
DATAMODEL_FIELD_OPEN_VARS = [
	"opendata", 	# pure open data - all publics can access
	"commons", 		# data with specific licence - i.e. all users of the platform
	"collective", 	# data only visible by the collectif - i.e. all users of the platform
	"private", 		# personal data - only accessible by logged specific user
]
OPEN_LEVEL_DICT = {
	"all" 			: ["opendata", "commons", "collective", "private"], 
	"collective"	: ["opendata", "commons", "collective"], 
	"commons" 		: ["opendata", "commons"],
	"opendata" 		: ["opendata"],
}

# fields to keep always as db backbone - mainly fields necessary to create a spider
DATAMODEL_CORE_FIELDS = [

	{"field_name" : "item_xpath", 		"field_type" : "url",	"field_open" : "commons" }, 	# spider-related
	{"field_name" : "item_list_xpath", 	"field_type" : "url",	"field_open" : "commons" }, 	# spider-related
	{"field_name" : "next_page", 		"field_type" : "text",	"field_open" : "commons" },		# spider-related
	{"field_name" : "follow_xpath",		"field_type" : "url", 	"field_open" : "commons" }, 	# spider-related

	{"field_name" : "spider_id", 		"field_type" : "text", 	"field_open" : "commons" },			# item-related = to be stored in item

	{"field_name" : "link_data", 		"field_type" : "url",	"field_open" : "opendata" },		# item-related = to be stored in item
	{"field_name" : "link_src", 		"field_type" : "url",	"field_open" : "opendata" },		# item-related = to be stored in item

	{"field_name" : "added_by", 		"field_type" : "email",	"field_open" : "private" },			# item-related = to be stored in item
	{"field_name" : "added_at", 		"field_type" : "date",	"field_open" : "opendata" },		# item-related = to be stored in item

	{"field_name" : "modified_by", 		"field_type" : "email",	"field_open" : "opendata" }, 	# spider-related
	{"field_name" : "modified_at", 		"field_type" : "date", 	"field_open" : "opendata" }, 	# spider-related
	
	# just for debugging purposes
	# {"field_name" : "testClass", 		"field_type" : "text"}		# item-related = to be stored in item
]
# item-related fields to be used for Item in GenericSpider, in addition to custom fields 
DATAMODEL_CORE_FIELDS_ITEM = [
	
	"link_data", 
	"link_src", 
	
	"spider_id", 

	"added_by", 
	"added_at", 

	"modified_by",
	"modified_at",

	# "testClass"
]
# TO DO / IMPLEMENT AT MAIN.PY : default fields for first 
DATAMODEL_DEFAULT_CUSTOM_FIELDS = [
	{"field_name" : "author",	"field_type" : "text", 	"field_open" : "opendata" },
	{"field_name" : "abstract", "field_type" : "text", 	"field_open" : "opendata" },
	{"field_name" : "tags", 	"field_type" : "tags", 	"field_open" : "opendata" },
	{"field_name" : "url", 		"field_type" : "url", 	"field_open" : "opendata" },
	{"field_name" : "image", 	"field_type" : "image", "field_open" : "opendata" },
]


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### CONTRIBUTORS ############################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

### radio buttons in 'edit contributor' form
CONTRIBUTOR_EDIT_FIELDS_RADIO = [
	"parse_follow", "page_needs_splash"
]
CONTRIBUTOR_EDIT_FIELDS_NUMBER = [
	"LIMIT", "download_delay", "page_count"
]
CONTRIBUTOR_EDIT_FIELDS_FLOAT = [
	"download_delay"
]
### to display form for edit contributor
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
			# "spidername" ,
			"start_urls",
			"item_xpath",
			"next_page",
			"parse_follow",
			"follow_xpath",
		], 
		"optional": [
			"page_needs_splash",
			"item_list_xpath",
		]
	 },

	# scraper - global advanced settings	
	"scraper_settings" : {
		"needed" : [
		],
		"optional" : [
			"LIMIT" 			,	# max number of pages to be crawled
			"download_delay" 	,	# delay
			# "page_count" 		,	# keep track of how many pages were crawled
		]
	},

}
CONTRIBUTOR_CUSTOMAZIBLE_FIELDS = CONTRIBUTOR_EDIT_FIELDS.keys()

### to instantiate contributor core fields in mongoDB
CONTRIBUTOR_CORE_FIELDS = {
	
	# scraper - custom infos 
	"infos" : {
		"name" 			: "" , 	# real name contributor
		"page_url" 		: "" ,	# domain to crawl
		"contact" 		: "",	# why did I put this field ?
		"notes" 		: " ",	# text area to store notes on the spider
		# "added_by" 	: "",
		# "modified_by" : "",
		# "is_working" 	: False
	},

	# scraper - custom for scraping basics
	 "scraper_config" : {
		"spidername" 		: "",		# automatically generated
		"start_urls" 		: [],		# list of urls to parse
		
		"item_list_xpath"	: "",		# xpath of items list on a page
		"item_xpath"		: "",		# xpath of each item on a page
		"next_page" 		: "",		# xpath to go to next page

		"parse_follow" 		: False,	# boolean to know if needs to follow link in page to get all infos
		"follow_xpath" 		: "",		# xpath to follow item's url to get all info on item

		"page_needs_splash" : False,	# if page needs jquery to be parsed
	},

	# scraper - custom for scraping xpaths 
	"scraper_config_xpaths" : {
		# ... will be filled with custom fields _id from "db.datamodel.find({"field_type":"custom"})"
	},

	# scraper - global settings	
	"scraper_settings" : {
		"LIMIT" 			: 100,	# max number of pages to be crawled
		"download_delay" 	: 0.1,	# delay
		"page_count" 		: 1,	# keep track of how many pages were crawled
	},

	# scraper - log and stats	
	"scraper_log" : {
		
		"added_by" 				: "",		# 
		"added_at" 				: None,		# 
		"modified_by" 			: "",		# 
		"modified_at" 			: None,		# 
		
		"is_working" 			: False,	# 
		"is_tested" 			: False,	# 
		"is_running" 			: False,	# 
		
		"error_array" 			: [],		# 
		
		"item_count" 			: 0,		# 
		"item_count_depth_1" 	: 0,		# 
	},

}

### create list of not fully customazible fields 
NOT_CUSTOM_DATAMODEL_FIELDS = []
for k, v in CONTRIBUTOR_CORE_FIELDS.iteritems() : 
	l = v.keys()
	for i in l : 
		NOT_CUSTOM_DATAMODEL_FIELDS.append(i)
# print "NOT_CUSTOM_DATAMODEL_FIELDS :", NOT_CUSTOM_DATAMODEL_FIELDS


"""
### !!! all those variables were moved to settings_queries.py

### DATA QUERIES FROM URL - reconstruct from slug
QUERY_DATA_BY_DEFAULT = {
	"page_n"			: 1,		# page number
	"results_per_page" 	: 25,		# self-explanatory
	"token"				: None, 	# TO DO LATER : client's JWT (token) to check permissions 
	"spider_id"			: ["all"], 	# spider_id for contributor(s)
	"is_complete"		: False, 	# only complete records
	"search_for"		: [],		# list of words to search in data collection
	"search_in"			: [],		# list of fields to search in
	"open_level"		: ["all"]	# fields of data to be shown -> "all" == "opendata" + "commons" + "private"
}
QUERIES_DATA_ALLOWED_UNIQUE = [
	"page_n", "results_per_page", "token", "is_complete", "open_level"
]
QUERIES_DATA_ALLOWED_INTEGERS  	= [
	"page_n", "results_per_page"
]
QUERIES_DATA_ALLOWED_BOOLEAN = [
	"is_complete"
]

### SPIDER QUERIES FROM URL - reconstruct from slug
QUERY_SPIDER_BY_DEFAULT = {
	"page_n"			: 1,		# page number
	"results_per_page" 	: 25,		# self-explanatory
	"token"				: None, 	# TO DO LATER : client's JWT (token) to check permissions 
	"spider_id"			: ["all"], 	# spider_id for contributor(s)
	"is_working"		: "any",	# 
}
QUERIES_SPIDER_ALLOWED_UNIQUE = [
	"page_n", "results_per_page", "token", "is_working"
]
QUERIES_SPIDER_ALLOWED_INTEGERS  	= [
	"page_n", "results_per_page"
]
QUERIES_SPIDER_ALLOWED_BOOLEAN = [
	
]
"""