#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time, sleep

import requests

import cal_scrap_wiki as g
from cal_db_manager import DBcore as db


def update_cal_db():
    for i in db.show_src():
        print 'LoadingYear: ' + str(i['year'])
        print 'LoadingPage: ' + i['url']
        sleep(1)
        time_change = time() - i['timestamp'] > 300
        if time_change and i['active']:
            print 'Time is changed.'
            head = requests.head(i['url'])
            page_available = head.status_code == 200
            page_change = head.headers['Last-Modified'] != i['modified_ts']
            print i['modified_ts']
            print head.headers['Last-Modified']
            if page_available and page_change:
                print 'Page is changed'
                sch_dict_list = g.scrap_sch(i['url'])
                db.update_sch(i['id'], sch_dict_list)
                i['modified_ts'] = head.headers['Last-Modified']
            else:
                print 'No need to update. Page is static.'
        else:
            print 'No need to update. Too Soon'
        i['timestamp'] = time()
        db.update_src(i)
    return


def _show_pf():
    list_pf = db.search_pf('PS4')
    for i in list_pf:
        print("%8s: %s" % ('title', i['title'].encode('utf-8')))
        print("%8s: %s, %s" % ('release', i['release'], i['year']))
        print("%8s: %s\n" % ('platform', ', '.join(i['platform'])))
    print len(list_pf)


if __name__ == '__main__':
    update_cal_db()
