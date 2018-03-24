# -*- encoding: utf-8 -*-


from settings_queries import *  # like QUERY_RESET, QUERY_DELETE, ...


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### GlOBAL CLEANING VARS ####################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

QUERY_TYPE = {
	"data" 			: "data",
	"contributors" 	: "contributors",
	"crawl" 		: "crawl"
}

### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### CLEANING STRINGS ########################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

STRIP_STRING			= u"\n\t"
DATA_CONTENT_TO_IGNORE 	= [ "", u"", u" ", u"-", u",", u", ", u"- "]
SYNONYMS_TRUE			= ["yes", "YES", "true", "True", "TRUE", "1", "t", "T"]
SYNONYMS_FALSE			= ["no", "NO", "false", "False", "FALSE", "0", "f", "F"]

### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### CLEANING SLUGS ##########################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

DEFAULT_ERROR_ARGS_TO_DELETE = [
	"error", 
	"_xsrf"
]

ERROR_ARGS_SPIDER_TO_IGNORE = DEFAULT_ERROR_ARGS_TO_DELETE + [ QUERY_RESET ] + [ QUERY_DELETE ] # + QUERY_SPIDER_BY_DEFAULT.keys()


### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###
### PAGINATION ##############################################################################
### + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + ###

PAGINATION_ARGS_TO_IGNORE = ["page_n", "error"]