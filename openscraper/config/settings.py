


""" APP SECRET KEY """
SECRET_KEY			= "app_very_secret_key"
WTF_CSRF_SECRET_KEY = "a_super_wtf_secret_key" ### needs to be the same than cis_front ?

### settings for openscrapper app
APP_PORT = 8000
APP_DEBUG = True 

### setting for cookies
COOKIE_SECRET = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E="
XSRF_ENABLED  = True 

### settings for MONGO_DB
MONGODB_HOST 		= "localhost"
MONGODB_PORT 		= 27017
MONGODB_DB          = "openscraper" ####
# collections
MONGODB_COLL_CONTRIBUTORS = "contributors" ####
MONGODB_COLL_DATAMODEL	  = "data_model"
MONGODB_COLL_DATASCRAPPED = "data_scraped"
MONGODB_COLL_USERS        = "users"