#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from difflib import SequenceMatcher
from time import time, sleep, mktime, strptime
from datetime import datetime
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
@click.option('--title', '-t', default='---')
@click.option('--platform', '-p', default='---')
@click.option('--year', '-y', default='2017')
@click.option('--timesection', '-ts', nargs=2, default=(0, 0), type=int)
@click.option('--alldata', '-a', default=False, is_flag=True)
@click.option('--export', '-e', default=False, is_flag=True)
@click.option('--noprint', default=False, is_flag=True)
def calshow(title, platform, year, timesection, alldata, export, noprint):
    """Show information in the database"""
    title_set = set()
    pf_set = set()
    year_set = set()
    time_set = set()
    final_set = set()
    final_list = []
    search_set_list = [title_set, pf_set, year_set, time_set]

    # Search Title
    def tt(val, tt):
        val = val.lower()
        tt = tt.lower()
        similarity = SequenceMatcher(None, val, tt).ratio() > 0.6
        superset = set(re.split(r': | ', val)).issuperset(tt.split(' '))
        subset = set(re.split(r': | ', val)).issubset(tt.split(' '))
        return similarity or superset or subset
    if title != '---':
        title_pool = db.search(Q.title.test(tt, title))
        [title_set.add(i['id']) for i in title_pool]

    # Search Platform
    def pf(val, pf):
        val = val.split(', ')
        return bool(set(val).issuperset(pf.split('&')))
    if platform != '---':
        for i in platform.split('|'):
            platform_pool = db.search(Q.platform.test(pf, i))
            [pf_set.add(j['id']) for j in platform_pool]

    # Search Year
    if year != '---':
        year_pool = db.search(Q.year == year)
        [year_set.add(i['id']) for i in year_pool]

    # Search Time Zone
    def tz(val):
        return True if tz_start <= val <= tz_stop else False
    if timesection != (0, 0):
        try:
            tz_start = mktime(strptime(str(timesection[0]), "%Y%m%d"))
            tz_stop = mktime(strptime(str(timesection[1]), "%Y%m%d"))
        except ValueError:
            tz_start = 0
            tz_stop = 0
        timesection_pool = db.search(Q.rls_ts.test(tz))
        [time_set.add(i['id']) for i in timesection_pool]

    # Return All Data
    def id_pool(val):
        return True if val in list(final_set) else False
    if alldata:
        final_list += db.search(Q.type == 'sched')
        final_list += db.search(Q.type == 'tba')
    else:
        final_set = title_set | pf_set | year_set | time_set
        for i in search_set_list:
            if i != set():
                final_set = final_set & i
        final_list = db.search(Q.id.test(id_pool))

    # No print
    calprint(final_list) if not noprint else False

    # Export ics file
    calexport(final_list) if not export else False

    return final_list


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


def calprint(final_list):
    """Print the result to screen."""
    for i in final_list:
        if i['type'] == 'tba':
            return
        print("%-8s: %s" % ('Title', i['title'].encode('utf-8')))
        print("%-8s: %s %s %s" % ('Release', i['month'], i['day'], i['year']))
        print("%-8s: %s\n" % ('Platform', i['platform']))
    return


def calexport(final_list):
    desc = ''
    with open('gamecores.ics', 'w') as f:
        f.write('BEGIN:VCALENDAR\n' +
                'PRODID:-//Gamecores//Gamecores Calendar//EN\n' +
                'VERSION:2.0\n' +
                'CALSCALE:GREGORIAN\n' +
                'X-WR-CALNAME:Gamecores\n')
    for i in final_list:
        if i['type'] == 'sched':
            event_time = datetime.fromtimestamp(i['rls_ts'])
            event_time = event_time.strftime('%Y%m%d')
        for kv in i['desc']:
            try:
                desc = desc + kv + ': ' + i['desc'][kv] + '\n'
            except TypeError:
                continue
        with open('gamecores.ics', 'a') as f:
            f.write('BEGIN:VEVENT\n' +
                    'DTSTART:' + event_time + '\n' +
                    'DTEND:' + event_time + '\n' +
                    'DESCRIPTION:' +
                    'Title: ' + i['title'].encode('utf-8') + '\\n' +
                    'Platform: ' + i['platform'].encode('utf-8') + '\n' +
                    'SUMMARY:' + i['title'].encode('utf-8') + '\n' +
                    'URL:' + i['url'].encode('utf-8') + '\n' +
                    'END:VEVENT\n')
    with open('gamecores.ics', 'a') as f:
        f.write('END:VCALENDAR\n')
    return


gc = click.CommandCollection(sources=[cal])
db = TinyDB(os.path.dirname(__file__) + '/cal_db.json')
Q = Query()

if __name__ == '__main__':
    # calinit()
    # calupdate()
    calshow()
    # calstat()
    # calexport(0)
