
"""
MAIN STRUCTURE FOR DB COLLECTIONS

MongoDB instantiated at Application level 

"""
import pprint

### USERS
### to initiate user core fields in mongoDB
USER_CORE_FIELDS = [
	
	"username",
	"email",
	"password", 	# needs to be hashed

	"level_admin",

	"organization",
	"organization_url",
	"picture",
	"logo",

	"preferences", 
	"uses", 
	"public_key"
]

### DATAMODEL 
### to initiate datamodel core fields in mongoDB
# fields type
DATAMODEL_FIELDS_TYPES = [
	"url", 
	"text", 
	"email", 
	"image", 
	"adress", 
	"date", 
	"tags", 
	"price"
]
# fields to keep always as db backbone - mainly fields necessary to create a spider
DATAMODEL_CORE_FIELDS = [
	{"field_name" : "next_page", 		"field_type" : "text"},	# spider-related
	{"field_name" : "follow_xpath", 	"field_type" : "url"}, 	# spider-related
	{"field_name" : "item_xpath", 		"field_type" : "url"}, 	# spider-related

	{"field_name" : "spider_id", 		"field_type" : "text"},		# item-related = to be stored in item

	{"field_name" : "link_data", 		"field_type" : "url"},		# item-related = to be stored in item
	{"field_name" : "link_src", 		"field_type" : "url"},		# item-related = to be stored in item

	{"field_name" : "added_by", 		"field_type" : "email"},	# item-related = to be stored in item
	{"field_name" : "added_at", 		"field_type" : "date"},		# item-related = to be stored in item

	{"field_name" : "modified_by", 		"field_type" : "email"}, 	# spider-related
	{"field_name" : "modified_at", 		"field_type" : "date"}, 	# spider-related
	
	{"field_name" : "testClass", 		"field_type" : "text"}		# item-related = to be stored in item
]
# item-related fields to be used for Item in GenericSpider, in addition to custom fields 
DATAMODEL_CORE_FIELDS_ITEM = [
	"link_data", 
	"link_src", 
	"spider_id", 
	"added_by", 
	"added_at", 

	"testClass"
]
# TO DO / IMPLEMENT AT MAIN.PY : default fields for first 
DATAMODEL_DEFAULT_CUSTOM_FIELDS = [
	{"field_name" : "author",	"field_type" : "text"},
	{"field_name" : "abstract", "field_type" : "text"},
	{"field_name" : "tags", 	"field_type" : "tags"},
	{"field_name" : "url", 		"field_type" : "url"},
]

### CONTRIBUTORS
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
			"next_page",
			"parse_follow",
			"follow_xpath",
			"item_xpath",
		], 
		"optional": [
			"page_needs_splash",
		]
	 },

}

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
		
		"item_xpath"		: "",		# xpath of each item on a page
		"next_page" 		: "",		# xpath to go to next page

		"parse_follow" 		: False,	# boolean to know if needs to follow link in page to get all infos
		"follow_xpath" 		: "",		# xpath to follow item's url to get all info on item

		"page_needs_splash" : False,	# if page needs jquery to be parsed
	},

	# scraper - custom for scraping xpaths 
	"scraper_config_xpaths" : {
		# ... will be filled with custom fields _ids from db.datamodel.find({"field_type":"custom"})
	},

	# scraper - global settings	
	"scraper_settings" : {
		"LIMIT" 			: 100,	# number of pages to be crawled
		"download_delay" 	: 0,	# delay
		"page_count" 		: 1,	# keep track of how many pages were crawled
	},

	# scraper - log and stats	
	"scraper_log" : {
		"added_by" 				: "",		# 
		"modified_by" 			: "",		# 
		"is_working" 			: False,	# 
		"error_array" 			: [],		# 
		"item_count" 			: 0,		# 
		"item_count_depth_1" 	: 0,		# 
	},

}

### create list of not fully customazible fields 
# NOT_CUSTOM_DATAMODEL_FIELDS = CONTRIBUTOR_CORE_FIELDS["scraper_config"].keys() +  CONTRIBUTOR_CORE_FIELDS["infos"].keys()
NOT_CUSTOM_DATAMODEL_FIELDS = []
for k, v in CONTRIBUTOR_CORE_FIELDS.iteritems() : 
	l = v.keys()
	for i in l : 
		NOT_CUSTOM_DATAMODEL_FIELDS.append(i)
# print "NOT_CUSTOM_DATAMODEL_FIELDS :", NOT_CUSTOM_DATAMODEL_FIELDS