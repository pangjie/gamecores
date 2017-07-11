# Gamecores
A video game information tool. 

## User Guide
Developing...

## Gamecores Devlog Live

### 1. Setup Project

1. Create Github Repository.  
    `git@github.com:pangjie/gamecores`
2. Clone to local.  
    `$ git clone git@github.com:pangjie/gamecores`
3. Create & Active Python virtual environment.
    `$ virtualenv .venv`
    `$ . .venv/bin/activate`
4. Python package structure building

### 2. Game Calendar

1. Create a module called `cal_scrape_wiki.py` to scrape game release date from wiki game.  
    `pip install requests`  
    `pip install beautifulsoup4`
    1. Create `scrape_sch(url)` to scrape release information from wiki and return a info-dictionary list. The info-dictionary has four elements: title, platform, release date, url.  
        + `sch(table)`
        + 
        + `usch(table)`
        + `gen_rls_ts(desc)`
    2. Create `fixer(key, value)` to format original information scraped from html. 
        + `fix_key(key)`
        + `fix_value(value)`
        + `fix_title(value)`
        + `fix_platform(value)`
        + `fix_date(value)`
    3. Create `extract_inforbox(url)` to extract details from urls of games' wiki pages. 
        + `pip install shortuuid`
        + `pip install tinydb`
        + The basic functions of this module include initial a database and add/remove/show/update/search data. 
2. Create a module called `cal_data_manager.py` to organize and manage data with `TinyDB`.
3. Create `cal_core.py` for handling everything about the game calendar data.

###  Pre-Publish `gamecores` In Pypi For Test

###  Game/Engine/Company WIKI Search

###  Game Industry Tree

###  Stroies from G-cores.com

