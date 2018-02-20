
from controller import *
# from admin import AdminHandler


### all routing functions are in controller.py
urls = [
    # (r"/", MainHandler),
    # (r"/test", TestHandler),

    ### main pages
    (r"/", MainHandler),
    (r"/recommended/", RecommendedHandler),
    (r"/edit/([0-9Xx\-]+)", BookEditHandler),
    (r"/add", BookEditHandler),

    # (r"/crawl/", CrawlerHandler )

    # (r"/admin", AdminHandler),    
]