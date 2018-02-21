

""" 
TEST FOR A GENERIC SPIDER 
-------------------------

"""

### import scrapy utilities
import scrapy
import scrapy.crawler as crawler

from multiprocessing import Process, Queue
from twisted.internet import reactor, defer

from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

s = get_project_settings()
# print dict(s)

runner = crawler.CrawlerRunner()


### import itmes
from items import ProjectItems

### define pipelines



#####################################################

### define generic spider
basic_spider_config = {
					"name"  : "quote", 
					"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],
				 } 

class GenericSpider(scrapy.Spider):
	
	def __init__(self, spider_config = basic_spider_config): 
		"""
		init spider with its config dict as an arg (from contributor datas in DB)
		"""
		self.name = spider_config["name"] # "quote"
		self.start_urls = spider_config["start_urls"] 
		
	def parse(self, response):
		for quote in response.css('div.quote'):
			print(quote.css('span.text::text').extract_first())



### define spider runner
def run_test_spider(run_spider_config = basic_spider_config):
	"""
	just launch run_test_spider() from any handler
	"""

	### configure custom spider from a config
	spider = GenericSpider( spider_config = run_spider_config )

	def f(q):
		try:
			### add crawler.runner as deferred
			deferred = runner.crawl(spider)
			# deferred = runner.crawl(self.spider)
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



