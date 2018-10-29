# -*- coding: utf-8 -*-

from 	tornado.log import enable_pretty_logging, LogFormatter, access_log, app_log, gen_log

gen_log.info("--> importing .mixins")

import scrapy
from scrapy import Spider 

### import base_fields #########
### inherit fields (data model) from somewhere (static dict or DB)
from . import base_fields



# class GenericSpiderMixin : 
class GenericSpiderMixin(Spider) : 
	
	"""Mixin class for the generic spider"""
	gen_log.info ("\n/// GenericSpiderMix root ")

	# def __init__(self, **kwargs) : 
	def __init__(self) : 

		gen_log.info ("\n/// GenericSpiderMix / init ")

		# Default fields for mixin class
		
		# self.name = ""  # The name of the spider to use when executing the spider

		self.error_array = []
		self.item_count = 0  # will be incremented each time a new item is created
		self.item_count_depth_1 = 0  # will be incremented each time an item is completed in detailed page
		self.LIMIT = 5  # The number of pages where the spider will stop
		self.page_count = 1  # The number of pages already scraped
		self.download_delay = 0  # The delay in seconds between each request. some website will block too many requests
		
		# fields at __init__ filled from spider_config ########################

		# self.page_url = ""  # base url (ex : "https://www.mysite.org")
		# self.label = ""
		# self.start_urls = []  # List of URLs that will be crawled by the parse method
		# self.list_css_selector = ""
		# self.next_page_xpath = ""

		# All the xpaths needed to fill the Item objects attributes
		# populate from base_fields
		# for field in base_fields : 
		# 	self.__dict__[field] = ""
		# self.img_xpath = ""
		# self.link_xpath = ""
		# self.abstract_xpath = ""
		# self.title_xpath = ""
		# self.date_xpath = ""

		# super(GenericSpiderMixin, self).__init__()

	### all generic extractor functions

	def get_title(self, action):
		return self.get_data(action, self.title_xpath, "title")

	def get_next_page(self, response):
		"""tries to find a new page to scrap.
		if it finds one, returns it along with a True value"""
		next_page = response.xpath(self.next_page_xpath).extract_first()
		if (next_page is not None) and (self.page_count < self.LIMIT):
			self.page_count += 1
			next_page = next_page.strip()
			next_page = self.add_string_to_complete_url_if_needed(next_page, self.page_url)
			return True, next_page
		else:
			return False, next_page

	def add_string_to_complete_url_if_needed(self, not_complete_url, rest_of_url=None):
		"""Adds the missing beggining part of an url with the '/' if needed"""
		if rest_of_url is None:
			rest_of_url = self.page_url
		if not not_complete_url.startswith("http"):
			if not not_complete_url.startswith("/"):
				not_complete_url = "{}{}".format("/", not_complete_url)
			not_complete_url = "{}{}".format(rest_of_url, not_complete_url)
		return not_complete_url

	def print_error(self):
		"""Will print all the Errors in the error_array"""
		if len(self.error_array) > 0:
			self.logger.info("\nErrors : \n")
			for error in self.error_array:
				self.logger.info("{}\n".format(error))

	def spider_closed(self, spider):
		"""Send some status to logging"""
		self.logger.info("**** Spider closed: {} ****".format(spider.name))
		self.logger.info("--- {} Items retrieved (main search page count)".format(self.item_count))
		self.logger.info("--- {} Items retrieved (detailed page count)".format(self.item_count_depth_1))
		self.logger.info("--- {} Pages crawled".format(self.page_count))
		self.print_error()
		self.logger.info("***End scraping***\n")