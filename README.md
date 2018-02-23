# SocialConnect : project OpenScraper
A generic Scrapy crawler wrapped in a Tornado framework with a nice interface, so almost anyone with very little technical knowledge could scrap public data and install/adapt it for its own purposes. 

... anyway that's the goal ...

----

#### **To which needs this project aims to answer ?**
Scraping can quickly become a mess, mostly if you need to scrap several websites in order to get a structured dataset eventually. So you need to set up several scrapers for every website, configure the spiders one by one, get the data from every website, and clean up the mess to get from this raw material one structured dataset you know that exists... Usually you have two choices : either use a proprietary service (like Apify), or write your own code (for instance based on BeautifulSoup or Scrapy), adapt it for your own purposes, and usually be the only one to be able to use it. 

To make that job a bit easier OpenScraper aims to display a GUI interface (client side) so you'll just have to set the field names (the data structure you exepct), then enter a list of websites to scrap, set up the xpath to scrap for each field, and finally click on a button to run the scraper configured for each website... 

#### **A theoretical use case**
So let's say you have a list of different websites you want to scrap projects from, each website having some urls where are listed projects (in my case social innovation projects). For every project you know it could be described with : a title, an abstract, an image, a list of tags, an url, and the name and url of the source website... So from OpenScraper you would have to : 
- specify the data structure you expect ("title", "abstract", etc...) ;
- add a new _contributor_ (a source website) : at least its _name_ and the _start_url_ from which you'll do the scraping ; 
- configure the spider for every _contributor_, i.e. specify the xpaths for every field (xpath for "title", xpath for "abstract", etc... );
- save the _contributor_ spider configuration, and click on the "run spider" button... 
- the data will be stored in the OpenScraper database (MongoDB), so you could later retrieve the structured data (with an API endpoint or in a tabular file)

---- 

### TECH GOALS
- Python asynchronous interface (Tornado) for Scrapy 
- store a list of url sources + corresponding xpaths in a DB (Mongo)
- web interface to edit the sources' xpath list
- display the list of sources + for each add a button to run the scraper
- store/extract results in the DB

### ROADMAP
1. understand basics of Tornado (reuse some tutorial material)
2. basic Tornado + MongoDB setup
3. understand basics of Scrapy
4. make Tornado and a basic scrapy spider work together (non-blocking)
5. create a generic spider (class)
6. integrate generic spider + tests + run
7. make a nice front in bootstrap 
8. ... nicer front in vue.js
9. GUI to edit also fields' names (structure of the scrapping)

------

### Notes
... work in progress @ step 1. : for now I'm just trying to adapt some Tornado tutorial into a server where Scrapy and Tornado are working well together (no CSS for now)

### CURRENTLY... 

- cleaning references to "books" (adapt tutorial to OpenScraper goals)
- running scrapy from browser with a basic generic crawler
- ...

-------

## Contact
Julien Paris (JPy)

-------

## WALKTHROUGH

1. **setup**

	> $ pip install -r requirements.txt


2. **run app** from `$ ~/../app_scrapnado`

	> $ python main.py


3. **check in your browser** at `localhost:8000`


3. **run the test spider in the browser** at `localhost:8000/crawl/testspider`

