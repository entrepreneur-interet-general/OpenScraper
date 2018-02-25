
### settings for openscrapper app
APP_PORT = 8000
APP_DEBUG = True 

### setting for cookies
COOKIE_SECRET = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E="
XSRF_ENABLED  = True 

### settings for MONGO_DB
MONGODB_HOST 		= "localhost"
MONGODB_PORT 		= 27017
MONGODB_DB          = "bookstore" ####
# collections
MONGODB_COLL_CONTRIBUTORS = "books" ####
MONGODB_COLL_DATAMODEL	  = "datamodel"
MONGODB_COLL_DATASCRAPPED = "projects"