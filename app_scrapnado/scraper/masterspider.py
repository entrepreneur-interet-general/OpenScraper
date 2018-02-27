
import pprint

### import scrapy utilities
import scrapy

from multiprocessing import Process, Queue
from twisted.internet import reactor, defer

from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


### settings scrapy

# s = get_project_settings()
# print "\ndefault settings scrapy : "
# pprint.pprint(dict(s))
# update settings from settings_scrapy.py
# s.update(dict(ITEM_PIPELINES={
# 	'openscraper.pipelines.RestExportPipeline': 300,
# }))
# print "\nupdated settings scrapy : "
# pprint.pprint(dict(s))

# runner = crawler.CrawlerRunner(settings=s)


### import base_fields ###############
### inherit fields (data model) from somewhere (static dict or DB)
# from . import base_fields

### import items
from items import * #GenericItem #, StackItem #ScrapedItem

### import mixins
# from mixins import GenericSpiderMixin

### define pipelines



#####################################################
"""
	error_array = []
	item_count = 0  # will be incremented each time a new item is created
	item_count_depth_1 = 0  # will be incremented each time an item is completed in detailed page
	LIMIT = 5  # The number of pages where the spider will stop
	page_count = 1  # The number of pages already scraped
	name = ""  # The name of the spider to use when executing the spider
	download_delay = 0  # The delay in seconds between each request. some website will block too many requests
	page_url = ""  # base url (ex : "https://www.mysite.org")
	label = ""
	start_urls = []  # List of URLs that will be crawled by the parse method
"""


#####################################################
### define generic spider
### cf : https://blog.scrapinghub.com/2016/02/24/scrapy-tips-from-the-pros-february-2016-edition/


from scrapy import Spider
from scrapy.spiders import SitemapSpider, CrawlSpider
from scrapy.crawler import CrawlerProcess, CrawlerRunner
import scrapy.crawler as crawler

# process = crawler.CrawlerRunner()


### UTILS
def dictFromDataModelList (datamodel_list ) : 
	"""create a correspondance dict from datamodel to _xpath like : {} """
	data_model_dict = { i : "{}_xpath".format(i) for i in datamodel_list }
	return data_model_dict


### ON ITEMS AND PIPELINES SEE : https://gist.github.com/alecxe/fc1527d6d9492b59c610

class GenericSpider(Spider) :
	
	"""a generic spider to be configured with datamodel and spider_config variables"""
	
	### spider class needs a default name
	name = "genericspider"

	def __init__(self, datamodel=None, spider_config=None, *args, **kwargs) : 
		
		### super init/override spider class with current args 
		print "\n--- GenericSpider / __init__ :"
		super(GenericSpider, self).__init__(*args, **kwargs)
		
		### store spider_config
		print "--- GenericSpider / spider_config :", spider_config
		self.spider_config = spider_config

		### getting data model for later use in item
		print "--- GenericSpider / datamodel :"
		self.datamodel = datamodel 
		pprint.pprint (self.datamodel)

		## storing a _xpath correspondance dict from datamodel
		print "--- GenericSpider / datamodel_dict :"
		self.datamodel_dict = dictFromDataModelList(datamodel)
		pprint.pprint(self.datamodel_dict)

		### getting all the config args from spider_config
		print "--- GenericSpider / passing kwargs..."
		for k, v in spider_config.iteritems() : 
			print "   - ", k, ":", v
			self.__dict__[k] = v

	'''
	def parse(self, response):
		"""
		parse pages to scrap data
		"""
		for scraped_data in response.css('div.quote'):
			
			### create Item to fill
			# item = ScrapedItem()
			item = self.custom_item
			
			### TO DO : fill item with results
			# self.fill_item_from_results_page(action, item)

			print(scraped_data.css('span.text::text').extract_first())

		is_next_page, next_page = self.get_next_page(response)
		if is_next_page:
			yield response.follow(next_page, callback=self.parse)

	def get_next_page(self, response, no_page_url):
		has_next_page = True
		has_not_next_page = False
		'''

	def parse(self, response):
		"""
		parse pages to scrap data
		"""
		for raw_data in response.xpath('//div[@class="quote"]'):
			
			### create Item to fill
			itemclass = create_item_class('GenericItemClass', self.datamodel)
			item = itemclass()
			# just for debugging purposes
			item['testClass'] = "class is tested"

			### extract data and feed it to item based on spider_config
			for d_model, d_xpath in self.datamodel_dict.iteritems() : 
				# first, checks if xpath exists in spider_config
				if d_xpath in self.spider_config : 
					# check if field is not empty
					if self.spider_config[d_xpath] != [] and self.spider_config[d_xpath] != "" :
						# fill item field corresponding to xpath
						item[ d_model ] = raw_data.xpath(self.spider_config[ d_xpath ]).extract()

			print "\nGenericSpider.parse - item : \n", item.items()
			# print item.keys()
			yield item

			if self.spider_config["parse_follow"] == True : 
				pass
				url = item['link']
				yield scrapy.Request(url, callback=self.parse_detailed_page, meta={'item': item})

		### get and go to next page 
		# next_page_url = response.xpath(self.spider_config[ "next_page_xpath" ]).extract_first()
		# if next_page_url is not None:
		# 	print "\n --- GenericSpider.parse / NEXT PAGE... \n"
		# 	# yield scrapy.Request(response.urljoin(next_page_url))
		# 	yield scrapy.follow(response.urljoin(next_page_url, callback=self.parse))

		is_next_page, next_page = self.get_next_page(response)
		if is_next_page:
			print "\n --- GenericSpider.parse / NEXT PAGE... \n"
			yield response.follow(next_page, callback=self.parse)


	def get_next_page(self, response):
		"""tries to find a new page to scrap.
		if it finds one, returns it along with a True value"""
		next_page = response.xpath(self.next_page_xpath).extract_first()
		if (next_page is not None) and (self.page_count < self.LIMIT):
			self.page_count += 1
			# next_page = next_page.strip()
			# next_page = self.add_string_to_complete_url_if_needed(next_page, self.page_url)
			next_page = response.xpath(self.spider_config[ "next_page_xpath" ]).extract_first()
			return True, next_page
		else:
			return False, next_page

	def add_string_to_complete_url_if_needed(self, not_complete_url, rest_of_url=None):
		"""adds the missing beggining part of an url with the '/' if needed"""
		if rest_of_url is None:
			rest_of_url = self.page_url
		if not not_complete_url.startswith("http"):
			if not not_complete_url.startswith("/"):
				not_complete_url = "{}{}".format("/", not_complete_url)
			not_complete_url = "{}{}".format(rest_of_url, not_complete_url)
		return not_complete_url

	def parse_item (self, response): 

		### create Item to fill
		itemclass = create_item_class('GenericItemClass', self.datamodel)
		item = itemclass()

		### just for debugging purposes
		item['testClass'] = "class is tested"

		### extract data and feed it to item based on spider_config
		for d_model, d_xpath in self.datamodel_dict.iteritems() : 
			# first, checks if xpath exists in spider_config
			if d_xpath in self.spider_config : 
				# fill item field corresponding to xpath
				item[ d_model ] = raw_data.xpath(self.spider_config[ d_xpath ]).extract()

		print "\nGenericSpider.parse - item : \n", item.items()
		# print item.keys()
		yield item



### define spider runner
### cf : https://stackoverflow.com/questions/13437402/how-to-run-scrapy-from-within-a-python-script
### cf : https://doc.scrapy.org/en/latest/topics/practices.html
### solution chosen from : https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable 

def run_generic_spider( spidername=None, datamodel=None, run_spider_config=None ):
	"""
	just launch run_generic_spider() from any handler in controller
	"""

	print "\n--- run_generic_spider / spidername : ", spidername
	print "--- run_generic_spider / run_spider_config : ", run_spider_config
	
	### instantiate settings and provide a custom configuration
	# settings = Settings()
	# settings.set('ITEM_PIPELINES', {
	# 	'__main__.JsonWriterPipeline': 100
	# })

	### initiating crawler process
	# process = CrawlerRunner() #CrawlerProcess()
	process = CrawlerRunner({
		'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
		# 'ITEM_PIPELINES' : '',
	})
	settings = get_project_settings()
	print "--- run_generic_spider / Your USER_AGENT is:\n%s" % (settings.get('USER_AGENT'))
	print "--- run_generic_spider / Your ITEM_PIPELINES is:\n%s" % (settings.get('ITEM_PIPELINES'))

	### adding crawler.runner as deferred
	def f(q):
		try:
			### send custom spider config from run_spider_config
			### cf : https://stackoverflow.com/questions/35662146/dynamic-spider-generation-with-scrapy-subclass-init-error
			deferred = process.crawl(GenericSpider, datamodel=datamodel, spider_config=run_spider_config )
			# deferred = process.crawl(ToScrapeSpiderXPath )
			
			deferred.addBoth(lambda _: reactor.stop())
			reactor.run()
			q.put(None)
		except Exception as e:
			q.put(e)

	### putting task in queue and start
	q = Queue() 
	p = Process(target=f, args=(q,))
	p.start()
	result = q.get()
	p.join()

	if result is not None:
		raise result






#############################################
### cool snippets 

	### convert to class object
	# spider = globals()[spider]