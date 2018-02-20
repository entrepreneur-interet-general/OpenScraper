# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class CisSpidersItem(Item):
    # define the fields for your item here like:
    # name = Field()
    idx         = Field()
    spider_name = Field()
    img         = Field()
    title       = Field()
    abstract    = Field()
    link        = Field()
    date        = Field()
    area        = Field()  # List
    key_words   = Field()  # List
    contact     = Field()
    video       = Field()  # List
    state       = Field()
    project_holder = Field()
    partner     = Field()
    economic    = Field()
    coordinates = Field()