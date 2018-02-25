
# -*- coding: utf-8 -*-

""" 
TOWARDS A GENERIC SPIDER 
-------------------------
"""

### need to be flexible : user set it and store structure in DB
### this common structure needs is to be used in  : 
### - scrapy item    : class ScrapedItem(scrapy.Item):
### - scrapy mixin   : class GenericSpiderMix : 
### - generic spider : class GenericSpider(scrapy.Spider, GenericSpiderMix):

### temporary solution (static list) 
base_fields = [
		"img_xpath" ,
		"link_xpath" ,
		"abstract_xpath" ,
		"title_xpath" ,
		"date_xpath" ,
]

### needs imports here to be called from controller.py
from items import *
from masterspider import *
