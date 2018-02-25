
import pprint

### import scrapy utilities
import scrapy

from multiprocessing import Process, Queue
from twisted.internet import reactor, defer

from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


### settings scrapy

s = get_project_settings()
print "\ndefault settings scrapy : "
pprint.pprint(dict(s))
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
# from items import GenericItem #ScrapedItem

### import mixins
# from mixins import GenericSpiderMixin

### define pipelines



#####################################################
### test spider configurations

"""
model spider_config dict : 

spider_config = {
	"spidername" : "...",
	"start_urls" : ['http://...'],

	for data_field in datamodel :
		data_field : xpath ...
}

"""

"""
spider_config_struct = {
	"name"  : "quote", 
	"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],

	"xpath_title" : "...",
	"xpath_abstract" : "...",
	"xpath_image" : "...",
} 
"""

### EXAMPLE FROM ORIGINAL SPIDER TO FACTORIZE
avise_spider_config = {
	
	"LIMIT" : 20,
	
	"name" : "avise",
	"label" : "Avise",

	"page_url" : "http://www.avise.org",
	"start_urls" : ['http://www.avise.org/portraits', ],

	"list_xpath_selector" : '//div[@class:"view-content"]//div[@onclick]',
	"next_page_xpath" : '//li[@class:"pager-next"]/a/@href',

	# 
	"img_xpath" : './/image/@*[name():"xlink:href"]',
	"link_xpath" : './/h2/a/@href',
	"abstract_xpath" : './/div[@class:"field-item even"]/text()',
	"title_xpath" : './/h2/a/text()',

	# In action page
	"date_xpath" : 	'//div[@class:"field field--name-field-created-year field--type-text field--label-inline ' \
				 	'clearfix"]//div[@class:"field-item even"]/text()',
	"area_xpath" : 	'//div[@class:"addressfield-container-inline locality-block country-FR' \
				 	'"]/span/text()',
	"key_words_xpath" : '//div[@class:"field field--name-field-portrait-domain ' \
					  'field--type-text field--label-inline clearfix"]' \
					  '//div[@class:"field-item even"]//text()',
	"contact_xpath" : '//div[@id:"node-portrait-full-group-portrait-coordonnees"]//text()',
	"video_xpath" : "",
	"state_xpath" : "",
	"project_holder_xpath" : '//div[@id:"node-portrait-full-group-portrait-coordonnees"]' \
							 '//div[@class:"name-block"]/text()',
	"partner_xpath" : "",
	"economic_xpath" : "",
}

#####################################################
### define generic spider
### cf : https://blog.scrapinghub.com/2016/02/24/scrapy-tips-from-the-pros-february-2016-edition/


from scrapy import Spider
from scrapy.spiders import SitemapSpider, CrawlSpider
from scrapy.crawler import CrawlerProcess, CrawlerRunner
import scrapy.crawler as crawler

# process = crawler.CrawlerRunner()

# class GenericSpider(GenericSpiderMixin) :
class GenericSpider(Spider) :
	
	"""a generic spider to be configured with spider_config variable"""
	
	### spider class needs a default name
	name = "genericspider"

	def __init__(self, custom_item=None, spider_config=None, *args, **kwargs) : 
		
		### super init/override spider class with current args 
		print "\n--- GenericSpider / spider_config :", spider_config
		super(GenericSpider, self).__init__(*args, **kwargs)

		### storing item
		self.custom_item = custom_item 

		### getting all the config args from spider_config
		print "--- GenericSpider / passing kwargs..."
		for k, v in spider_config.iteritems() : 
			print "   - ", k, ":", v
			self.__dict__[k] = v

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

	# def get_next_page(self, response):
	# 	"""tries to find a new page to scrap.
	# 	if it finds one, returns it along with a True value"""
	# 	next_page = response.xpath(self.next_page_xpath).extract_first()
	# 	if (next_page is not None) and (self.page_count < self.LIMIT):
	# 		self.page_count += 1
	# 		next_page = next_page.strip()
	# 		next_page = self.add_string_to_complete_url_if_needed(next_page, self.page_url)
	# 		return True, next_page
	# 	else:
	# 		return False, next_page

### define spider runner
### cf : https://stackoverflow.com/questions/13437402/how-to-run-scrapy-from-within-a-python-script
### cf : https://doc.scrapy.org/en/latest/topics/practices.html
### solution chosen from : https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable 

def run_generic_spider( spidername=None, custom_item=None, datamodel=None, run_spider_config=None ):
	"""
	just launch run_generic_spider() from any handler in controller
	"""

	print "\n--- run_generic_spider / spidername : ", spidername
	print "--- run_generic_spider / run_spider_config : ", run_spider_config
	
	### initiating crawler process
	process = CrawlerRunner()
	# process = CrawlerProcess({
	# 	'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
	# })

	### adding crawler.runner as deferred
	def f(q):
		try:
			### send custom spider config from run_spider_config
			### cf : https://stackoverflow.com/questions/35662146/dynamic-spider-generation-with-scrapy-subclass-init-error
			deferred = process.crawl(GenericSpider, item=custom_item, spider_config=run_spider_config )
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