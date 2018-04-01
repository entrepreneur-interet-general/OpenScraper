
### settings for openscrapper app
APP_PORT        = 8000
APP_DEBUG       = True 
APP_PROD       	= False 

if APP_DEBUG == True :
	APP_AUTORELOAD  = True  # test
else : 
	APP_AUTORELOAD  = False # prod


### setting for cookies
COOKIE_SECRET = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E="
XSRF_ENABLED  = True 


### settings for MONGO_DB
if APP_PROD == False :
	MONGODB_HOST 		= "localhost"
elif APP_PROD == True :
	MONGODB_HOST 		= "0.0.0.0"
MONGODB_PORT 			= 27017
MONGODB_DB          	= "openscraper" 
MONGODB_APP_URI     	= "mongodb://{}:{}".format(MONGODB_HOST, MONGODB_PORT)


# collections
MONGODB_COLL_CONTRIBUTORS = "contributors"
MONGODB_COLL_DATAMODEL	  = "data_model"
MONGODB_COLL_DATASCRAPPED = "data_scraped"
MONGODB_COLL_USERS        = "users"

