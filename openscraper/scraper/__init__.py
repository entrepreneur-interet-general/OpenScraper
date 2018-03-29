
# -*- coding: utf-8 -*-

""" 
TOWARDS A GENERIC SCRAPER 
-------------------------
the goal of this part of OpenScraper is to use 
the Scrapy library but free of its usual/out-of-the-box configuration

all the scraping is rewritten to be used in a self-contained manner
so to be run from the python script and not from bash

"""


### needs imports here to be called from controller.py
from items              import *
from masterspider       import *
from pipelines          import *
from settings_scrapy	import *