# -*- encoding: utf-8 -*-


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