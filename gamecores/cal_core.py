#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time, sleep

import requests

import cal_scrape_wiki as g
from cal_data_manager import DBcore as db


def update_cal_db():
    for i in db.show_src():
        print 'LoadingYear: ' + str(i['year'])
        print 'LoadingSource: ' + i['url']
        if time() - i['update_ts'] > 30 and i['active']:
            i['update_ts'] = time()
            head = requests.head(i['url'])
            page_available = head.status_code == 200
            page_changed = head.headers['Last-Modified'] != i['modified_ts']
            print i['modified_ts']
            print head.headers['Last-Modified']
            if page_available and page_changed:
                print 'Page is changed'
                sch_dict_list = g.scrape_sch(i['url'])
                db.update(i['id'], sch_dict_list)
                i['modified_ts'] = head.headers['Last-Modified']
            else:
                print 'Page is not changed by last update.'
        else:
            print 'Update too often'
        db.update_src(i)
        sleep(1)
    return


def show():
    list_pf = db.search('platform', 'PS4')
    for i in list_pf:
        print("%8s: %s" % ('title', i['title'].encode('utf-8')))
        print("%8s: %s, %s" % ('release', i['release'], i['year']))
        print("%8s: %s\n" % ('platform', ', '.join(i['platform'])))
    print len(list_pf)


if __name__ == '__main__':
    print db.show_src()
    update_cal_db()
