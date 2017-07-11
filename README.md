# Gamecores
A video game information tool. 

## User Guide
Developing...

## Gamecores Devlog Live

### 1. Setup Project

1. Create Github Repository 
   `git@github.com:pangjie/gamecores`
2. Clone to local
   1. `$ git clone git@github.com:pangjie/gamecores`
3. Create & Active Python virtual environment.
   `$ virtualenv .venv`
   `$ . .venv/bin/activate`
4. Python package structure building

### 2. Game Calendar

1. Create a module called `cal_scrape_wiki.py` to scrape game release date from wiki game.
   `pip install requests`
   `pip install beautifulsoup4`
   1. Create `scrape_sch(url)` to scrape release information from wiki and return a info-dictionary list. The info-dictionary has four elements: title, platform, release date, url.
      * [x] `sch(table)`
      * [x] `usch(table)`
      * [x] `gen_rls_ts(desc)`
   2. Create `fixer(key, value)` to format original information scraped from html.
      * [x] `fix_key(key)`
      * [x] `fix_value(value)`
      * [x] `fix_title(value)`
      * [x] `fix_platform(value)`
      * [x] `fix_date(value)`
   3. Create `extract_inforbox(url)` to extract details from urls of games' wiki pages.
      * `pip install shortuuid`
      * `pip install tinydb`
      * The basic functions of this module include initial a database and add/remove/show/update/search data. 
2. Create a module called `cal_data_manager.py` to organize and manage data with `TinyDB`.
3. Create `cal_core.py` for handling everything about the game calendar data.

###  Publish `gamecores` in Pypi

###  Game/Engine/Company WIKI Search

###  Game Industry Tree

###  Stroies from G-cores.com

