


<h1 align=center>  OpenScraper</h1>

<h4 align=center> a public service for webscraping</h4>

<h2 align=center>
	<img src="./openscraper/static/images/logo_openscraper.png">
</h2>

<p align=justify>
OpenScraper is an open source webscraper with a simple interface, <b>so almost anyone with very little technical knowledge could scrap public data</b> and install/adapt it for its own purposes... for free.</p>

<p align=center>... anyway, that's the goal folks ! ... <br>(it's a development phase for now)</p>


<h4 align=center> OpenScraper is a project by <a href=https://entrepreneur-interet-general.etalab.gouv.fr/defi/2017/09/26/socialconnect/ >SocialConnect</a></h4>

<p align=center>#python #tornado #scrapy #mongodb #bulma</p>

----
## ARGUMENT

#### **To which needs this project aims to answer ?**
Scraping can quickly become a mess, mostly if you need to scrap several websites in order to eventually get a structured dataset. Usually you need to set up several scrapers for every website, configure the spiders one by one, get the data from every website, and clean up the mess to get from this raw material one structured dataset you know that exists... 

#### **Yes, similar solutions already does exist... but...**
So you have mainly three options when it come to scrap the web : 
- either use a proprietary and quite expensive service (like [Apify](https://www.apify.com/) or [import.io](https://www.apify.com/)) and depend on an external service ;
- ask a friend if you are lucky, ask a developer or a company to do it for you if you have money for that...
- or if you have the know-how write your own code (for instance based on BeautifulSoup or Scrapy), adapt it for your own purposes, and usually be the only one (I mean the only developer around) to be able to use/adapt it.

#### **A theoretical use case**
So let's say you are a **researcher**, a **journalist**, a **public servant** in an administration, a member of any **association** who want to survey some evolutions in the society... Let's say you need data not easy to get, and you can't afford to spend thousand of euros in using a private service for webscraping. 

You'd have a list of different websites you want to scrap similar information from, each website having some urls where are listed those data (in our first case social innovation projects). For every information you know it could be similarly described with : a title, an abstract, an image, a list of tags, an url, and the name and url of the source website, and so on... 

So from OpenScraper you would have to : 
- specify the data structure you expect ("_title_", "_abstract_", etc...) ;
- add a new _contributor_ (a source website) : at least its _name_ and the _start_url_ from which you'll do the scraping ; 
- configure the spider for every _contributor_, i.e. specify the xpaths for every field (xpath for "title", xpath for "abstract", etc... );
- save the _contributor_ spider configuration, and click on the "run spider" button... 
- the data will be stored in the OpenScraper database (MongoDB), so you could later retrieve the structured data (with an API endpoint or in a tabular format like a .csv file)

#### **An open scraper for more digital commons**
To make that job a bit easier (and far cheaper) OpenScraper aims to display an online GUI interface (a webapp on the client side) so you'll just have to set the field names (the data structure you expect), then enter a list of websites to scrap, for each one set up the xpath to scrap for each field, and finally click on a button to run the scraper configured for each website... 

... and tadaaaa, you'll have your data : you will be able able to import it, share it, and visualize it (at least we're working on it as quickly as we can)... 

OpenScraper is developped in open source, and will provide a documentation as much as a legal framework (licence and CGU) aiming to make the core system of OpenScraper fit the [RGPD](https://en.wikipedia.org/wiki/General_Data_Protection_Regulation), in the letter and in the spirit. 


-------

## INSTALLATION WALKTHROUGH

1. **clone or download the repo**
1. **install MongoDB locally** or get the URI of the MongoDB you're using
1. **go to your openscraper folder**
1. **setup (without virtual environment)**

	> $ pip install -r requirements.txt

1. **update the `config/settings.py` file** with your mongoDB URI (if you're not using default mongoDB connection)

1. **run app** from `$ ~/../app_scrapnado`

	> $ python main.py

1. **check in your browser** at `localhost:8000`

1. **create/update your datamodel** at `localhost:8000/datamodel/edit`

1. **create/update your spiders** at `localhost:8000/contributors`

1. **run the test spider in the browser** at `localhost:8000/crawl/testspider`

------

### TECH STACK
- _Language_ : **Python**... because let's be honest, I don't manage so many languages for that kind of project
- _Backend_  : **Tornado** [(link)](http://www.tornadoweb.org/en/stable/)... one of the few async/non-blocking Python frameworks
- _Scraping_ : **Scrapy** [(link)](https://scrapy.org/), perhaps with **Selenium for Python** [(link)](http://selenium-python.readthedocs.io/) inside or **splash** for jquery follow-up...
- _Frontend_ : **Bulma** [(link)](https://bulma.io/) (to make it nice) and then **Vue.js** [(link)](https://vuejs.org/) (to make it async)

### TECH GOALS FOR THE MVP
- web interface to edit the data structure
- Python asynchronous interface (Tornado) for Scrapy 
- store a list of url sources + corresponding xpaths in a DB (Mongo)
- web interface to edit the sources' xpath list
- display the list of sources + for each add a button to run the scraper
- store/extract results in the DB

----- 

### ROADMAP FOR MVP
1. understand basics of Tornado (reuse some tutorial material)
1. basic Tornado + MongoDB setup
1. understand basics of Scrapy
1. UI to create user (register), create/update a datamodel, create/update a spider configuration
1. create a generic spider (class) + generic item to fill, both callable from handlers
1. integrate generic spider + tests + run
1. make Tornado and a basic scrapy spider work together (non-blocking)
1. add a GUI to configure the data structure you expect from the scraping
1. make a nice front in Bulma 
1. ... nicer front in vue.js
1. GUI to edit also fields' names (structure of the scrapping)


------

### CURRENTLY... 
- currently at step /4 - /5
- running scrapy from browser with a basic generic crawler
- create item to fill on the fly (genericItem)
- ...

### Notes / issues
- the generic spider need to be tested on various websites configurations
- must add a feature to use Selenium inside a spider if needed (ajax or .click function)



-------
## Credits 

- the [SocialConnect](https://entrepreneur-interet-general.etalab.gouv.fr/defi/2017/09/26/socialconnect/) project, aka "Carrefour des Innovations Sociales"
- the [EIG](https://entrepreneur-interet-general.etalab.gouv.fr/) program by [Etalab](https://www.etalab.gouv.fr/)
- [CGET](http://www.cget.gouv.fr/)

--------
## Contacts

- [Julien Paris](<mailto:julien.paris@cget.gouv.fr>) (aka [JPy](https://twitter.com/jparis_py) on Twitter)

---------

## Screenshots

![alt text](./screenshots/openscraper_v0.1_beta-index.png "index")

![alt text](./screenshots/openscraper_v0.1_beta-edit_datamodel.png "index")

![alt text](./screenshots/openscraper_v0.1_beta-list_scrapers.png "index")