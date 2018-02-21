# SocialConnect_openscrapper
A Scrapy generic crawler wrapped in a Tornado framework with a nice interface ... at least that's the goal...

---- 

### GOALS
- Python asynchronous interface (Tornado) for Scrapy 
- store a list of url sources + corresponding xpaths in a DB (Mongo)
- web interface to edit the sources' xpath list
- display the list of sources + for each add a button to run the scrapper
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
... work in progress @ step 1. : for now I'm just trying to adapt some Tornado tutorial

### CURRENTLY... 

- cleaning references to "books" (adapt tutorial to OpenScrapper goals)
- trying to run scrapy  

-------

## Contact
Julien Paris (JPy)

-------

## WALKTHROUGH

1. setup 

    > $ pip install -r requirements.txt

2. run app

    ... from /app_scrapnado

    > $ python main.py

    ... check in the browser at `localhost:8000`
   