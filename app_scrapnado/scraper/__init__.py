

""" 
TESTS FOR A GENERIC SPIDER 
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
# print "settings : " , dict(s)

runner = crawler.CrawlerRunner()


### import itmes
from items import ProjectItems


### define pipelines



#####################################################

### define generic spider
basic_spider_config = {
					"name"  : "quote", 
					"start_urls" : ['http://quotes.toscrape.com/tag/humor/'],

					"xpath_title" : "...",
					"xpath_abstract" : "...",
					"xpath_image" : "...",
				 } 
# @gen.coroutine
class GenericSpider(scrapy.Spider):
	
	def __init__(self, spider_config = basic_spider_config): 
		"""
		init spider with its config dict as an arg (from contributor datas in DB)
		"""
		### main arguments
		self.name = spider_config["name"] 
		self.start_urls = spider_config["start_urls"] 
		
		### parsing arguments
		### ...
		
		### custom xpaths
		###...

	def parse(self, response):
		"""
		parse pages to scrap innovative projects
		"""
		for project in response.css('div.quote'):
			print(project.css('span.text::text').extract_first())








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





