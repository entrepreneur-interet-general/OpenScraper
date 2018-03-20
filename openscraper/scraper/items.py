# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item
from scrapy.item import DictItem, Field

'''
# basic scrapy Item instance
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
'''

class GenericItem(Item) : 

	"""generic scrapy.Item populated with scrapy.Field() from a list"""

	def __init__(self, datamodel_list, *args, **kwargs ) : 
		
		print "::: GenericItem - datamodel_list : ", datamodel_list
		super(GenericItem, self).__init__(*args, **kwargs)
		
		for field in datamodel_list : 
			self.__dict__[field] = scrapy.Field()


### cf : https://github.com/scrapy/scrapy/issues/398
def create_item_class(class_name, fields_list):

	"""generic Item class creator populated from a list"""

	fields_dict = {}
	for field_name in fields_list:
		fields_dict[field_name] = Field()
	return type( str(class_name), (DictItem,), {'fields': fields_dict} )

