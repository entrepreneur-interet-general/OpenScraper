# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ProjectItems(scrapy.Item):
    idx = scrapy.Field()
    spider_name = scrapy.Field()
    img = scrapy.Field()
    title = scrapy.Field()
    abstract = scrapy.Field()
    link = scrapy.Field()
    date = scrapy.Field()
    area = scrapy.Field()  # List
    key_words = scrapy.Field()  # List
    contact = scrapy.Field()
    video = scrapy.Field()  # List
    state = scrapy.Field()
    project_holder = scrapy.Field()
    partner = scrapy.Field()
    economic = scrapy.Field()
    coordinates = scrapy.Field()