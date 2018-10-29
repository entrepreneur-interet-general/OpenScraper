
from scrapy.core.downloader.handlers.http import HttpDownloadHandler 

class HttpsDownloaderIgnoreCNError (HttpDownloadHandler) : 
	
	def __init__(self, *args, **kwargs):

		super(HttpsDownloaderIgnoreCNError, self).__init__(*args, **kwargs)