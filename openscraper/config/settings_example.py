


# # """ APP SECRET KEY """
# SECRET_KEY			= "app_very_secret_key"
# WTF_CSRF_SECRET_KEY = "a_super_wtf_secret_key" ### needs to be the same than cis_front ?

### settings for openscrapper app
APP_PORT		= 8000
APP_DEBUG		= True 
APP_PROD		= False 

if APP_DEBUG == True :
	APP_AUTORELOAD  = True  # test
else : 
	APP_AUTORELOAD  = False # prod


### setting for cookies
WTF_CSRF_SECRET_KEY = "a_super_wtf_secret_key"
XSRF_ENABLED  		= True 


### settings for MONGO_DB

MONGODB_HOST 		= "localhost"
# if APP_PROD == False :
# 	MONGODB_HOST 		= "localhost"
# elif APP_PROD == True :
# 	MONGODB_HOST 		= "0.0.0.0"
MONGODB_PORT 			= 27017
MONGODB_DB				= "openscraper" 
MONGODB_APP_URI			= "mongodb://{}:{}".format(MONGODB_HOST, MONGODB_PORT)


# collections
MONGODB_COLL_CONTRIBUTORS = "contributors"
MONGODB_COLL_DATAMODEL	  = "data_model"
MONGODB_COLL_DATASCRAPPED = "data_scraped"
MONGODB_COLL_USERS        = "users"

