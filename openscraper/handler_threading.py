# -*- encoding: utf-8 -*-

"""
BIG THANKS TO LUCAS COSTA / https://gist.github.com/lucascosta
this decorator saved my life !!!
https://gist.github.com/lucascosta/4ddd0afadfee75398536cb4125a8732b

a decorator to deal with background tasks 
and running them from a queue ...

"""

# cf : http://www.tornadoweb.org/en/stable/faq.html#my-code-is-asynchronous-but-it-s-not-running-in-parallel-in-two-browser-tabs
# cf : https://gist.github.com/methane/2185380 
# cf : https://gist.github.com/lucascosta/4ddd0afadfee75398536cb4125a8732b

import 	types

from 	concurrent.futures import ThreadPoolExecutor
from 	datetime import timedelta
from 	tornado import gen
from 	tornado.concurrent import run_on_executor

# import settings for Tornado
from config.settings_threading import *


# main decorator for running scrapy operations as background tasks
def onthread(function):	
	
	@gen.coroutine
	def decorated(self, *args, **kwargs):
		
		future = executed(self, *args, **kwargs)
		
		try:
			response = yield gen.with_timeout(
				timedelta(seconds=THREADPOOL_TIMEOUT_SECS), future)

			if isinstance(response, types.GeneratorType):  # subthreads
				
				response = yield gen.with_timeout(
					timedelta(seconds=THREADPOOL_TIMEOUT_SECS),
					next(response))
		
		except gen.TimeoutError as exc:
			future.cancel()
			raise exc
		
		self.write(response)

	@run_on_executor
	def executed(*args, **kwargs):
		return function(*args, **kwargs)


	return decorated