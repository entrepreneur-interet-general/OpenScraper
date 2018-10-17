# -*- encoding: utf-8 -*-

"""
MAIN STRUCTURE FOR DB COLLECTIONS

MongoDB instanciated at Application level 

"""
import pprint


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### OPEN DATA LEVELS ########################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

# need to be compatible with DATAMODEL_FIELD_OPEN_VARS
OPEN_LEVEL_DICT = {
	"admin"			: ["opendata", "commons", "collective", "private", "admin"], 
	"collective"	: ["opendata", "commons", "collective", "private"], 
	"commons" 		: ["opendata", "commons", ],
	"opendata" 		: ["opendata"],
}

### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### USERS ###################################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

USER_AUTH_LEVELS = {
	"admin"   	: {	"datamodel" 	: "all", 
					"contributors"	: "all", 	
					"data" 			: "admin"  
					}, 	# can modify and view everything
	"staff"		: {	"datamodel" 	: "own", 
					"contributors" 	: "own", 	
					"data" 			: "collective"  
					},		# can modify its own fields in datamodel, can modify its own spiders
	"user"	  	: {	"datamodel" 	: "none", 
					"contributors" 	: "own", 	
					"data" 			: "commons"  
					},		# cannot modify fields in datamodel, can modify its own spiders
	"visitor" 	: {	"datamodel" 	: "none", 
					"contributors" 	: "none", 	
					"data" 			: "opendata" 
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
	"url", 		# href
	"text", 	# default
	"email", 	# mailto
	"image", 	# src
	"adress", 
	"date", 	# datetime
	"tags", 
	"integer",
	"float",
	"price",
	"list"		# note : not sure about this one ... 
]

# field_keep options in form only
DATAMODEL_FIELD_KEEP_VARS = [
	"keep", "not visible", "delete", 
]
DATAMODEL_FIELD_OPEN_VARS = [
	"opendata", 	# pure open data - all publics can access
	"commons", 		# data with specific licence - i.e. all users of the platform
	"collective", 	# data only visible by the collective - i.e. not all users of the platform
	"private", 		# personal data - only accessible by logged specific user
]

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

	{"field_name" : "page_n", 			"field_type" : "integer", "field_open" : "opendata" },		# item-related = to be stored in item
	{"field_name" : "item_n", 			"field_type" : "integer", "field_open" : "opendata" },		# item-related = to be stored in item

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

	"page_n", 
	"item_n", 

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
	"parse_follow", 
	# "page_needs_splash", 
	# "deploy_list", 
	"parse_reactive",
	"parse_api",
]
CONTRIBUTOR_EDIT_FIELDS_RADIO_TEXTS = {
	"parse_follow" 		: ["The data is complete in the list ","I need to click a link in the list to show the complete data "] , 
	"parse_reactive" 	: ["The website is not reactive","The website is reactive"] , 
	"parse_api"			: ["The website has no API", "The website has an API"],
	# "page_needs_splash" : ["no","yes"], 
	# "deploy_list" 		: ["There is no special button at the end of the list","There is a 'show more button' at the end of the list"]
}
CONTRIBUTOR_EDIT_FIELDS_NUMBER = [
	"LIMIT_PAGES", 
	"LIMIT_ITEMS",

	"download_delay", 

	"wait_driver" 	,	# delay for ajax response wait
	"wait_page" 	,	# delay for new page response wait
	"wait_implicit" ,	# delay for implicit response wait

	"page_count"
]
CONTRIBUTOR_EDIT_FIELDS_FLOAT = [
	"download_delay",

	"wait_driver" 	,	# delay for ajax response wait
	"wait_page" 	,	# delay for new page response wait
	"wait_implicit" ,	# delay for implicit response wait

]
### to display form for edit contributor
CONTRIBUTOR_EDIT_FIELDS = {

	### fields displayed in "edit contributor" page
	### "needed" = to be displayed
	### "optional" = optional (in drawer) - TO DO 

	# custom infos 
	"infos" : {
		"needed" : [
			"name", 			# spider name
			"licence",			# licence of all data scrapped by this spider
			"page_url",			# root url 
			"logo_url",			# logo's url of the website
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
			# "deploy_list",
			# "deploy_list_xpath",
			"parse_follow",
			"follow_xpath",
			"parse_reactive",

			"parse_api",
			"api_pagination_root",
			# "api_url_root",
		], 
		"optional": [
			# "page_needs_splash",
			"item_list_xpath",
		]
	 },

	# scraper - global advanced settings	
	"scraper_settings" : {
		"needed" : [
		],
		"optional" : [
			"LIMIT_PAGES" 			,	# max number of pages to be crawled
			"LIMIT_ITEMS" 		,	# max number of items to be scraped

			"download_delay" 	,	# delay

			"wait_driver" 		,	# delay for ajax response wait
			"wait_page" 		,	# delay for new page response wait
			"wait_implicit" 	,	# delay for implicit response wait

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
		"licence"	 	: "",	# licence of all data scrapped by this spider
		"logo_url"		: "" ,	# url for contributor's logo
		"contact" 		: "" ,	# why did I put this field ?
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
		
		# "deploy_list"		: False,	# selenium action to click on "show more" button if exists
		# "deploy_list_xpath"	: "",		# xpath to click on if "show more" button exists... 

		# "page_needs_splash" : False,	# if page needs jquery to be parsed
		"parse_reactive" 	: False,	# if page needs javascript to be parsed
	
		"parse_api"			: False,	# use the website's API to get data 
		"api_pagination_root" : "",
		# "api_url_root"	: "",
	},

	# scraper - custom for scraping xpaths 
	"scraper_config_xpaths" : {
		# ... will be filled with custom fields _id from "db.datamodel.find({"field_type":"custom"})"
	},

	# scraper - global settings	
	"scraper_settings" : {

		"LIMIT_PAGES" 				: 100,	# max number of pages to be crawled
		"LIMIT_ITEMS" 			: 0,	# max number of items to be scraped 
		
		"download_delay" 		: 0.25,	# delay
		
		"wait_driver" 			: 5.0,	# delay for ajax response wait
		"wait_page" 			: 1.5,	# delay for new page response wait
		"wait_implicit" 		: 0.5,	# delay for implicit response wait
		
		"page_count" 			: 1,	# keep track of how many pages were crawled
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