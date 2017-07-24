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
    desc_list_tba = []
    scheduled_list = []
    tba_list = []
    year = re.findall(r'20\d\d', url)[0]
    page = requests.get(url).content
    soup = bs4.BeautifulSoup(page, "html.parser")
    tbls = soup.find_all('table', class_='wikitable')
    year_with_th = ['2010', '2015', '2016', '2017', '2018']
    year_with_tr = ['2008', '2009', '2011', '2012', '2013', '2014']
    for tb in tbls:
        if year in year_with_th:
            col = [x.get_text() for x in tb.find_all('th')]
        elif year in year_with_tr:
            col = [x.get_text() for x in tb.find('tr').find_all('td')]
        if col[2:3] in [[u'Title']]:
            desc_list += sch(tb, col)
        elif col[2:3] in [[u'Platforms'], [u'Platform(s)']]:
            desc_list_tba += unsch(tb)
    [desc_list.remove(x) for x in desc_list if 'Month' in x]
    scheduled_list = [data_washer(x, year) for x in desc_list]
    tba_list = [tba_data_washer(x, year) for x in desc_list_tba]
    for i in scheduled_list + tba_list:
        try:
            # print i[5]
            # print i[4].encode('utf-8')
            # print i
            pass
        except IndexError:
            pass
    # return desc_list + desc_list_tba
    # return desc_list
    print year
    return {'scheduled': scheduled_list, 'tba': tba_list}


def data_washer(x, year):
    key = ['rls_ts', 'year', 'month', 'day', 'title', 'platform', 'url']
    ref = re.compile(r'^(\[\d+\])+$|\[\w*\s\w*\]')
    if year in ['2017', '2018']:
        [x.remove(x[4]) for i in x if re.match(ref, x[4]) is not None]
    elif year in ['2015', '2016']:
        x.remove(x[4])
    elif year in ['2011']:
        x[3] = x[3] + ', ' + x[4]
        x.remove(x[4])
    x.insert(0, year)
    x.insert(0, gen_rls_ts(x))
    x[4] = fix_title(x[4])
    return dict(zip(key, x))


def tba_data_washer(x, year):
    key = ['year', 'title', 'release', 'platform', 'genre', 'url']
    x[0] = fix_title(x[0])
    x.insert(0, year)
    return dict(zip(key, x))


def sch(table, col):
    """
    Find game infomation from tables including exact release date.
    """
    stack = []
    stack_list = []
    col_n = len(col)
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    tags = [x for x in table.find_all('td')]
    items = [x.get_text().replace('\n', '') for x in tags]
    for idx, i in enumerate(items):
        if i.lower() in months:
            del stack[:]
        elif re.match(r'^\d+$|TBA', i) is not None:
            i = u'30' if i == 'TBA' else i
            if int(i) < 32:
                del stack[1:]
        stack.append(i)
        try:
            stack[col_n - 1]
            sub_url = tags[idx - col_n + 3].find('a').get('href')
            stack.append('https://en.wikipedia.org' + sub_url)
            stack_list.append(list(stack))
            del stack[2:]
        except AttributeError:
            stack.append('')
            stack_list.append(list(stack))
            del stack[2:]
        except IndexError:
            pass
    return stack_list


def unsch(table):
    """
    Find game infomation from tables without exact release date.
    """
    stack_list = []
    tags = [x for x in table.find_all('td')]
    items = [x.get_text().replace('\n', '') for x in tags]
    for i in range(0, len(items), 5):
        value = [items[i + x] for x in range(4)]
        try:
            sub_url = tags[i].find('a').get('href')
            value.append('https://en.wikipedia.org' + sub_url)
        except AttributeError:
            value.append('')
        stack_list.append(value)
    return stack_list


def gen_rls_ts(desc):
    try:
        return mktime(strptime(desc[0] + desc[1] + desc[2], "%Y%B%d"))
    except ValueError:
        return 0


def fix_value(value):
    """
    Format value of elements in desc-dict.
    """
    value = re.sub(r'\[\w*\d*\]|\s*\(\s*\w*\s*\)', '', value)
    value = re.sub(r'(\n)+', '\n', value).strip('\n')
    value = re.sub('\\xa0', ' ', value)
    return value


def fix_title(value):
    """
    Format title string.
    """
    value = fix_value(value)
    value = re.sub(r'\s*-\s*Wikipedia|\s*\(\d*\s*video game\)', '', value)
    value = re.sub(r';', ':', value)
    value = re.sub(r'\n', ' ', value)
    return value


if __name__ == '__main__':
    # print 'Run scrape_sch as Main'
    # year = raw_input('Please input a year between 2007-2018:')
    # url = 'https://en.wikipedia.org/wiki/' + year + '_in_video_gaming'
    # x = scrape_sch(url)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2008_in_video_gaming')
    # sleep(3)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2009_in_video_gaming')
    # sleep(3)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2010_in_video_gaming')
    # sleep(3)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2011_in_video_gaming')
    # sleep(3)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2012_in_video_gaming')
    # sleep(3)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2013_in_video_gaming')
    # sleep(3)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2014_in_video_gaming')
    # sleep(3)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2015_in_video_gaming')
    # sleep(3)
    # x = scrape_sch('https://en.wikipedia.org/wiki/2016_in_video_gaming')
    # sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2017_in_video_gaming')
    sleep(3)
    x = scrape_sch('https://en.wikipedia.org/wiki/2018_in_video_gaming')
    # sleep(3)
    # for i in x:
    #     print("%8s: %s" % ('title', i['title']))
    #     print("%8s: %s, %s" % ('release', i['release'], i['year']))
    #     print("%8s: %s\n" % ('platform', ', '.join(i['platform'])))
