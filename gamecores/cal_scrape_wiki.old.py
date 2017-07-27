#!/usr/bin/env python
# -*- coding: utf-8 -*-


from time import *
import re

import requests
import bs4


def scrape_sch(url):
    """
    Scrap schedule information form URL(wiki/20XX_in_vedio_gamming).
    Find all schedule tables whoes html lable class containing wikitable.
    """
    desc_list = []
    year = int(re.findall(r'20\d\d', url)[0])
    page = requests.get(url).content
    soup = bs4.BeautifulSoup(page, "html.parser")
    tbls = soup.find_all('table', class_='wikitable')
    for tb in tbls:
        if 2015 <= year <= 2018:
            col = [x.get_text() for x in tb.find_all('th')]
        elif 2008 <= year <= 2014:
            col = [x.get_text() for x in tb.find('tr').find_all('td')]
        if col[2:3] in [[u'Title']]:
            desc_list += sch(tb, len(col))
        elif col[2:3] in [[u'Platforms'], [u'Platform(s)']]:
            desc_list += unsch(tb, len(col))
    [x.update({'year': year}) for x in desc_list]
    [x.update({'rls_ts': gen_rls_ts(x)}) for x in desc_list]
    return desc_list


def sch(table, col_n):
    """
    Find game infomation from tables including exact release date.
    """
    re_pf = r"""PC\W|Win\W|Mac\W|Lin\W|
                |PPC$|Win$|Mac$|Lin$|Linux|
                |iOS|Android|Droid|WP\W|WP$|Apple Watch|
                |XBO$|XBO\W|X360|Xbox 360|
                |PS\d$|PS\d\W|PSV$|PSV\W|PSVita|PSN|PSP|PlayStation|
                |Wii\s*U|NS|3DS|N3DS|DSiWare|
                |HTC Vive|Oculus Rift"""
    prog_pf = re.compile(re_pf)
    desc_list, desc = [], {}
    months = ['january', 'february', 'march',
              'april', 'may', 'june',
              'july', 'august', 'september',
              'october', 'november', 'december']
    tags = [x for x in table.find_all('td')]
    items = [x.get_text().replace('\n', '') for x in tags]

    stack = []

    for i in items:
        if i.lower() in months:
            del stack[:]
            stack.append(i)
        elif re.match(r'^\d+$', i) is not None:
            # print stack
            del stack[1:]
            stack.append(i)
        else:
            stack.append(i)
        if len(stack) == col_n:
            # print stack
            del stack[2:]

    for idx, val in enumerate(items):
        if val.lower() in months:
            month = val
        elif re.match(r'^\d+$|TBA', val) is not None:
            day = val
        elif re.match(r'^\[\d+\]$|\[\w*\s\w*\]', val) is not None:
            pass
        elif re.match(prog_pf, val) is not None:
            desc['platform'] = fix_platform(val)
            desc['release'] = month + ' ' + day
            desc_list.append(dict.copy(desc))
        else:
            desc['title'] = fix_title(val)
            try:
                sub_url = tags[idx].find('a').get('href')
                desc['url'] = 'https://en.wikipedia.org' + sub_url
            except AttributeError:
                desc['url'] = ''
    return desc_list


def unsch(table, col_n):
    """
    Find game infomation from tables without exact release date.
    """
    desc_list = []
    keys = ['title', 'release', 'platform', 'genre', 'url']
    tags = [x for x in table.find_all('td')]
    items = [x.get_text().replace('\n', '') for x in tags]
    for i in range(0, len(items), 5):
        value = [fixer(keys[x], items[i + x]) for x in range(4)]
        try:
            sub_url = tags[i].find('a').get('href')
            value.append('https://en.wikipedia.org' + sub_url)
        except AttributeError:
            value.append('')
        desc_list.append(dict(zip(keys, value)))
        print value
    return desc_list


def gen_rls_ts(desc):
    time_str = desc['release'] + str(desc['year'])
    try:
        return mktime(strptime(time_str, "%B %d%Y"))
    except ValueError:
        return 0


def scrap_info_wiki(url):
    """
    May abandon this funciton.
    Not used.
    """
    root_url = 'https://en.wikipedia.org'
    game_list = []
    desc_list = []
    try:
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        list_div = soup.find('div', class_="mw-category").find_all('a')
        game_list += [root_url + x.get('href') for x in list_div]
    except AttributeError:
        return desc_list

    for item in game_list:
        desc = extract_infobox(item)
        desc_list.append(desc) if bool(desc) else 'Empty Dict.'
        print desc['title'] + ': Complete!'
        sleep(10)
    return desc_list


def extract_infobox(url):
    """
    The URL is a detail-info page of a game.
    """
    desc = {}
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    info = soup.find('table', class_='infobox')
    items = info.find_all('tr') if info is not None else []
    try:
        desc['title'] = items[0].find('th', class_='fn').get_text()
    except (AttributeError, IndexError):
        desc['title'] = soup.find('title').get_text()
    desc['title'] = fixer('title', desc['title'])
    for item in items:
        try:
            key = fix_key(item.find('th').get_text())
            value = item.find('td').get_text()
            desc[key] = fixer(key, value)
        except AttributeError:
            pass
    return desc


def fixer(key, value):
    """
    Format value of elements in desc-dict
    """
    if key == 'title':
        return fix_title(value)
    elif key == 'platform':
        return fix_platform(value)
    elif key == 'release':
        return fix_date(value)
    elif key == 'genre':
        return fix_value(value)
    else:
        return fix_value(value)


def fix_key(key):
    """
    A part of fixer()
    Format key of elements in desc-dict
    """
    key = fix_value(key).lower()
    key = re.sub(r'composers*|music by', 'music', key)
    key = re.sub(r'platforms', 'platform', key)
    key = re.sub(r'genres', 'genre', key)
    key = re.sub(r'developers', 'developer', key)
    key = re.sub(r'released*( date)*', 'release', key)
    key = re.sub(r'directed by', 'director', key)
    key = re.sub(r'produced by', 'producer', key)
    key = re.sub(r'publishe(d by)*(rs)*|distributor', 'publisher', key)
    key = re.sub(r'written by', 'writer', key)
    return key


def fix_value(value):
    """
    A part of fixer()
    Format value of elements in desc-dict
    """
    value = re.sub(r'\[\w*\d*\]|\s*\(\s*\w*\s*\)', '', value)
    value = re.sub(r'(\n)+', '\n', value).strip('\n')
    value = re.sub('\\xa0', ' ', value)
    return value


def fix_title(value):
    """
    A part of fixer()
    """
    value = fix_value(value)
    value = re.sub(r'\s*-\s*Wikipedia|\s*\(\d*\s*video game\)', '', value)
    value = re.sub(r';', ':', value)
    value = re.sub(r'\n', ' ', value)
    return value


def fix_platform(value):
    """
    A part of fixer()
    """
    value = fix_value(value)
    value = re.sub('\n', ', ', value)
    value = re.sub(r'PlayStation\s', 'PS', value)
    value = re.sub(r'Portable|Vita', 'V', value)
    value = re.sub(r',*\.*\sVita', ', PSV', value)
    value = re.sub(r'Vita', 'V', value)
    value = re.sub(r'PS\s4', 'PS4', value)
    value = re.sub(r'Xbox\sOne', 'XBO', value)
    value = re.sub(r'Xbox 360|^360|\s360', 'X360', value)
    value = re.sub(r'macOS|OS\sX', 'Mac', value)
    value = re.sub(r'\w*\sWindows|Win', 'PC', value)
    value = re.sub(r'Nintendo\sSwitch', 'NS', value)
    value = re.sub(r'Nintendo\s3DS', '3DS', value)
    value = re.sub(r'Wii\s*U', 'WiiU', value)
    value = re.sub(r'Droid', 'Android', value)
    value = re.sub(r'(Amazon\s)*Fire', 'Amazon Fire', value)
    value = re.sub(r'Linux', 'Lin', value)
    value = re.sub(r'Consoles|\sand\s|\s*&\s*|\sWorlds', '', value)
    value = re.sub(r'Lin XBO', 'Lin, XBO', value)
    value = re.sub(r'X360 PSP', 'X360, PSP', value)
    value = re.sub(r'WiiU X360', 'WiiU, X360', value)
    value = re.sub(r'mobile', 'iOS', value)
    value = re.split(r', |,|\. |\.', value)
    return value


def fix_date(value):
    """
    A part of fixer()
    """
    value = fix_value(value)
    value = re.sub(r'Q1', 'Spring', value)
    value = re.sub(r'Q2', 'Summer', value)
    value = re.sub(r'Q3', 'Autumn', value)
    value = re.sub(r'Q4', 'Winter', value)
    value = re.sub(u'\u2014', 'TBA', value)
    value = re.sub(r'^$', 'TBA', value)
    return value


if __name__ == '__main__':
    print 'Run scrape_sch as Main'
    # year = raw_input('Please input a year between 2007-2018:')
    # url = 'https://en.wikipedia.org/wiki/' + year + '_in_video_gaming'
    # x = scrape_sch(url)
    x = scrape_sch('https://en.wikipedia.org/wiki/2008_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2009_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2010_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2011_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2012_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2013_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2014_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2015_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2016_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2017_in_video_gaming')
    sleep(3)
    # for i in x:
    #     print("%8s: %s" % ('title', i['title']))
    #     print("%8s: %s, %s" % ('release', i['release'], i['year']))
    #     print("%8s: %s\n" % ('platform', ', '.join(i['platform'])))
