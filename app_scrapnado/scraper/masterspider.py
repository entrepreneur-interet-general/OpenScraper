
### import scrapy utilities
import scrapy
import scrapy.crawler as crawler

from multiprocessing import Process, Queue
from twisted.internet import reactor, defer

from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

s = get_project_settings()
# print "settings : " , dict(s)

runner = crawler.CrawlerRunner()


### import base_fields ###############
### inherit fields (data model) from somewhere (static dict or DB)
from . import base_fields

### import items
from items import ScrapedItem

### import mixins
from mixins import GenericSpiderMix 

### define pipelines



#####################################################
### test spider configurations

basic_spider_config = {
	"name"  : "quote", 
	"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],

	"xpath_title" : "...",
	"xpath_abstract" : "...",
	"xpath_image" : "...",
} 

avise_spider_config = {
	
	"LIMIT" : 20,
	
	"name" : "avise",
	"label" : "Avise",

	"page_url" : "http://www.avise.org",
	"start_urls" : ['http://www.avise.org/portraits', ],

	"list_xpath_selector" : '//div[@class:"view-content"]//div[@onclick]',
	"next_page_xpath" : '//li[@class:"pager-next"]/a/@href',

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

class GenericSpider(scrapy.Spider, GenericSpiderMix):
	
	def __init__(self, datamodel = [] , spider_config=basic_spider_config): 
		"""
		init spider with its config dict as an arg (from contributor datas in DB)
		"""

		print "--- GenericSpider / spider_config : ", spider_config

		### main arguments
		# self.name		= spider_config["name"] 
		# self.start_urls = spider_config["start_urls"] 
		for k, v in spider_config.iteritems() : 
			print k, ":", v
			self.__dict__[k] = v

		### parsing arguments
		self.get_next_page = ""
		### ...
		
		### custom xpaths
		###...

	def parse(self, response):
		"""
		parse pages to scrap innovative projects
		"""
		for scraped_data in response.css('div.quote'):
			
			### create Item to fill
			item = ScrapedItem()
			
			### fill item 
			# self.fill_item_from_results_page(action, item)

			print(scraped_data.css('span.text::text').extract_first())

		is_next_page, next_page = self.get_next_page(response)
		if is_next_page:
			yield response.follow(next_page, callback=self.parse)


	def get_next_page_bis(self, response, no_page_url):
		has_next_page = True
		has_not_next_page = False





### define spider runner
### cf : https://stackoverflow.com/questions/13437402/how-to-run-scrapy-from-within-a-python-script
### cf : https://doc.scrapy.org/en/latest/topics/practices.html
### solution chosen from : https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable 

def run_generic_spider(run_spider_config = basic_spider_config):
	"""
	just launch run_generic_spider() from any handler in controller
	"""

	### configure custom spider from a config
	spider = GenericSpider( spider_config = run_spider_config )

	def f(q):
		try:
			### add crawler.runner as deferred
			deferred = runner.crawl(spider)
			deferred.addBoth(lambda _: reactor.stop())
			reactor.run()
			q.put(None)
		except Exception as e:
			q.put(e)

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