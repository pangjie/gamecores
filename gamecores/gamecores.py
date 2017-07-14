#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from time import time, sleep
import requests

from shortuuid import uuid
from tinydb import *
import click

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
def calupdate():
    """Update data of actived years """
    print("Star to update database...")
    for i in db.search(Q.type == 'cal_src'):
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
        sch_list = g.scrape_sch(i['url'])
        # Remove expired data from db.
        db.remove((Q.type == 'sch') & (Q.src_id == i['id']))
        # Add data features to new data.
        data_patch = {'type': 'sch', 'src_id': i['id']}
        [j.update(data_patch) for j in sch_list]
        # Insert new data to db.
        db.insert_multiple(sch_list)
        # Update source data to db.
        i['update_ts'] = time()
        i['modified_ts'] = head.headers['Last-Modified']
        db.update(i, (Q.type == 'cal_src') & (Q.year == i['year']))
        sleep(1)
    print("Update Finished!")
    return


@cal.command()
@click.option('--title', default='')
@click.option('--platform', default='NS&PS4|NS')
def calsearch(title, platform):
    """Show information in the database"""
    print("Trying to show something")
    print title
    print platform.split('|')

    # Search Platform
    # def pf(val, pf):
    #     # print list(pf)
    #     return bool(set(val).intersection(pf.split('|')))

    # if platform != '':
    #     for i in db.search(Q.platform.test(pf, platform)):
    #         print i['title'].encode('utf-8')

    def xpf(val, pf):
        # print list(pf)
        return bool(set(val).issuperset(pf.split('&')))

    # if xplatform != '':
    #     for i in db.search(Q.platform.test(xpf, xplatform)):
    #         print i['title'].encode('utf-8')

    # if '&' in platform:
    #     for i in db.search(Q.platform.test(xpf, xplatform)):
    #         print i['title'].encode('utf-8')

    # if '|' in platform:
    #     for i in db.search(Q.platform.test(pf, platform)):
    #         print i['title'].encode('utf-8')
    pfset = set()
    for i in platform.split('|'):
        [pfset.add(j['title']) for j in db.search(Q.platform.test(xpf, i))]
        # for j in x:
        #     platform_set.add(j['url'])
    print pfset
    return


@cal.command()
def calexport():
    """Export calendar data to a ics file."""
    print("tring to generate an ics file")
    return


gc = click.CommandCollection(sources=[cal])
db = TinyDB(os.path.dirname(__file__) + '/cal_db.json')
Q = Query()

if __name__ == '__main__':
    # calinit()
    # calupdate()
    calsearch()
