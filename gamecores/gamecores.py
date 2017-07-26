#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from difflib import SequenceMatcher
from time import time, sleep, mktime, strptime
import re

from shortuuid import uuid
from tinydb import *
import click
import requests

import cal_scrape_wiki as g


@click.group()
def cal():
    return


@cal.command()
def calinit():
    """Clean and initialize the database file."""
    print("Start to init...")
    # Clean database.
    db.purge()
    # Build and insert wiki source data.
    src = {
        'type': 'cal_src',
        'active': True,
        'modified_ts': '',
        'update_ts': 0,
        'year': 0,
        'id': '',
        'url': '',
    }
    for i in xrange(2008, 2019):
        src['url'] = 'https://en.wikipedia.org/wiki/' +\
                     str(i) + '_in_video_gaming'
        src['year'] = i
        src['id'] = uuid(src['url'])
        db.insert(src)
    print("Init Fineshed!")
    return


@cal.command()
@click.option('--deep', default=False, is_flag=True)
def calupdate(deep):
    """Update data of actived years """
    print("Star to update database...")
    for i in db.search(Q.type == 'cal_src'):
        # Deep update or only update data after 2017
        if not deep and i['year'] < 2017:
            print 'Jump to next year'
            continue
        # In case user updates too often or a source is not active.
        if time() - i['update_ts'] < 30 or not i['active']:
            print 'Update too often'
            continue
        # In case the page isn't available or isn't changed.
        head = requests.head(i['url'])
        page_available = head.status_code == 200
        page_changed = head.headers['Last-Modified'] != i['modified_ts']
        if not page_available or not page_changed:
            print 'Page is not changed by last update.'
            continue
        # Get the newest schedual from source urls.
        schedualed_tba = g.scrape_sch(i['url'])
        sch_list = schedualed_tba['scheduled']
        tba_list = schedualed_tba['tba']
        print len(sch_list)
        print len(tba_list)
        # Remove expired data from db.
        db.remove((Q.type == 'sched') & (Q.src_id == i['id']))
        db.remove((Q.type == 'tba') & (Q.src_id == i['id']))
        # Add data features to new data.
        schedualed_data_patch = {'type': 'sched', 'src_id': i['id']}
        tba_data_patch = {'type': 'tba', 'src_id': i['id']}
        [j.update(schedualed_data_patch) for j in sch_list]
        [j.update(tba_data_patch) for j in tba_list]
        # Insert ID for each data
        [j.update({'id': uuid()}) for j in sch_list]
        [j.update({'id': uuid()}) for j in tba_list]
        # Insert new data to db.
        db.insert_multiple(sch_list)
        db.insert_multiple(tba_list)
        # Update source data to db.
        i['update_ts'] = time()
        i['modified_ts'] = head.headers['Last-Modified']
        db.update(i, (Q.type == 'cal_src') & (Q.year == i['year']))
        sleep(1)
    print("Update Finished!")
    return


@cal.command()
@click.option('--title', default='---')
@click.option('--platform', '-p', default='---')
@click.option('--year', '-y', default='---')
@click.option('--timesection', '-t', nargs=2, default=(0, 0), type=int)
@click.option('--alldata', default=False, is_flag=True)
def calsearch(title, platform, year, timesection, alldata):
    """Show information in the database"""
    title_set = set()
    pf_set = set()
    year_set = set()
    time_set = set()
    final_set = set()
    search_set_list = [title_set, pf_set, year_set, time_set]

    # Return All Data
    if not alldata:
        alldata_list = []
        alldata_list += db.search(Q.type == 'sched')
        alldata_list += db.search(Q.type == 'tba')
        for i in alldata_list:
            print i
        return alldata_list

    # Search Title
    def tt(val, tt):
        val = val.lower()
        tt = tt.lower()
        similarity = SequenceMatcher(None, val, tt).ratio() > 0.6
        superset = set(re.split(r': | ', val)).issuperset(tt.split(' '))
        subset = set(re.split(r': | ', val)).issubset(tt.split(' '))
        return similarity or superset or subset
    [title_set.add(i['title']) for i in db.search(Q.title.test(tt, title))]

    # Search Platform
    def pf(val, pf):
        return bool(set(val).issuperset(pf.split('&')))
    for i in platform.split('|'):
        [pf_set.add(j['title']) for j in db.search(Q.platform.test(pf, i))]

    # Search Year
    [year_set.add(i['title']) for i in db.search(Q.year == year)]

    # Search Time Zone
    try:
        tz_start = mktime(strptime(str(timesection[0]), "%Y%m%d"))
        tz_stop = mktime(strptime(str(timesection[1]), "%Y%m%d"))
    except ValueError:
        tz_start = 0
        tz_stop = 0

    def tz(val, timesection):
        return True if tz_start <= val <= tz_stop else False
    timesection_result = db.search(Q.rls_ts.test(tz, timesection))
    [time_set.add(i['title']) for i in timesection_result]

    # Final Set
    final_set = title_set | pf_set | year_set | time_set
    for i in search_set_list:
        if i != set():
            final_set = final_set & i
    print final_set
    for i in final_set:
        xx = db.search(Q.title == i)
        for xxx in xx:
            print xxx
    return final_set


@cal.command()
def calexport():
    """Export calendar data to a ics file."""
    print("tring to generate an ics file")
    return


@cal.command()
def calstat():
    """Satisfaction Section"""
    total = 0
    for i in xrange(2008, 2019):
        sum_year = len(db.search(Q.year == str(i)))
        print('Year: %s  Sum: %s' % (i, sum_year))
        total += sum_year
    print('Statistic: %s' % total)
    return


gc = click.CommandCollection(sources=[cal])
db = TinyDB(os.path.dirname(__file__) + '/cal_db.json')
Q = Query()

if __name__ == '__main__':
    # calinit()
    # calupdate()
    calsearch()
    # calstat()
