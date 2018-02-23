# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ScrapedItem(scrapy.Item):
	"""inherited from Makina Corpus' POC"""

	idx = scrapy.Field()
	spider_name = scrapy.Field()
	
	img = scrapy.Field()
	title = scrapy.Field()
	abstract = scrapy.Field()
	link = scrapy.Field()
	area = scrapy.Field()  # List
	key_words = scrapy.Field()  # List
	contact = scrapy.Field()
	video = scrapy.Field()  # List
	state = scrapy.Field()
	project_holder = scrapy.Field()
	partner = scrapy.Field()
	economic = scrapy.Field()
	coordinates = scrapy.Field()

	date = scrapy.Field()


class GenericItem(scrapy.Item) : 

	"""generic Item populated from a list"""

	def __init__(self, datamodel_list ) : 
		
		self.date = scrapy.Field()

		for i in datamodel_list : 
			self.__dict__[i] = scrapy.Field()


