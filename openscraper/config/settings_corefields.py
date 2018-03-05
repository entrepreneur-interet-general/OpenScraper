
"""
MAIN STRUCTURE FOR DB COLLECTIONS

MongoDB instantiated at Application level 

"""
import pprint

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


### to initiate datamodel core fields in mongoDB
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
		"page_url" 		: "" ,
		"contact" 		: "",
		"notes" 		: "",
		# "added_by" 		: "",
		# "modified_by" 		: "",
		# "is_working" 	: False
	},

	# scraper - custom for scraping basics
	 "scraper_config" : {
		"spidername" 		: "",
		"start_urls" 		: [],
		"parse_follow" 		: False,
		"next_page" 		: "",
		"follow_xpath" 		: "",
		"page_needs_splash" : False,
	},

	# scraper - custom for scraping xpaths
	"scraper_config_xpaths" : {
		# "next_page_xpath" : None,
	},

	# scraper - global settings	
	"scraper_settings" : {
		"LIMIT" 			: 100,
		"download_delay" 	: 0,
		"page_count" 		: 1,
	},

	# scraper - log and stats	
	"scraper_log" : {
		"added_by" 				: "",
		"modified_by" 			: "",
		"is_working" 			: False,
		"error_array" 			: [],
		"item_count" 			: 0,
		"item_count_depth_1" 	: 0
	},

}

### create list of not fully customazible fields 
# NOT_CUSTOM_DATAMODEL_FIELDS = CONTRIBUTOR_CORE_FIELDS["scraper_config"].keys() +  CONTRIBUTOR_CORE_FIELDS["infos"].keys()
NOT_CUSTOM_DATAMODEL_FIELDS = []
for k, v in CONTRIBUTOR_CORE_FIELDS.iteritems() : 
	l = v.keys()
	NOT_CUSTOM_DATAMODEL_FIELDS.append(l)