#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from shortuuid import uuid
from tinydb import *


class DBcore(object):
    """
    docstring for DBcore
    """
    db = TinyDB(os.path.dirname(__file__) + '/cal_db.json')
    Q = Query()

    def __new__(cls):
        """
        As a database operator class, the DBcore need to be a Single Module.
        """
        if not hasattr(cls, '_inst'):
            cls._inst = super(DBcore, cls).__new__(cls)
        return cls._inst

    @classmethod
    def init_db(cls):
        """
        Initialize database.
        """
        # Clean database.
        cls.db.purge()
        # Build and insert wiki source data.
        src = {}
        src['type'] = 'wiki_src'
        src['active'] = True
        src['modified_ts'] = ''
        src['update_ts'] = 0
        for i in xrange(2008, 2019):
            src['url'] = 'https://en.wikipedia.org/wiki/' +\
                         str(i) + '_in_video_gaming'
            src['year'] = i
            src['id'] = uuid(src['url'])
            cls.db.insert(src)
        return

    @classmethod
    def add_src(cls, year):
        """
        Active the wiki source of the year.
        """
        cls.db.update({'active': True},
                      (cls.Q.type == 'wiki_src') &
                      (cls.Q.year == year))
        return

    @classmethod
    def rm_src(cls, year):
        """
        Deactive the wiki source of the year.
        Clean the data from the wiki source.
        """
        cls.db.update({'active': False},
                      (cls.Q.type == 'wiki_src') &
                      (cls.Q.year == year))
        cls.db.remove((cls.Q.type == 'sch') &
                      (cls.Q.year == year))
        return

    @classmethod
    def update_src(cls, src_dict):
        """
        Update wiki source data such as update_ts and modified_ts.
        """
        cls.db.update(src_dict,
                      (cls.Q.type == 'wiki_src') &
                      (cls.Q.year == src_dict['year']))
        return

    @classmethod
    def show_src(cls):
        """
        Show every wiki source page.
        """
        return cls.db.search(cls.Q.type == 'wiki_src')

    @classmethod
    def update(cls, id, sch_dict_list):
        """
        Replace the old schedule data with new schedule data.
        id: The wiki source id.
        sch_dict_list: The list with the latest data.
        """
        # Remove the old data.
        cls.db.remove((cls.Q.type == 'sch') & (cls.Q.src_id == id))
        # Add data features to new data.
        [i.update({'type': 'sch', 'src_id': id}) for i in sch_dict_list]
        # Insert new data.
        cls.db.insert_multiple(sch_dict_list)
        return

    @classmethod
    def show(cls):
        """
        Return schedule data in the database.
        """
        return cls.db.search(where('type') == 'sch')

    @classmethod
    def search(cls, filed, *args):
        """
        Return the schedule data who contain platforms in *args.
        """
        def pf(val, pf):
            return bool(set(val).intersection(list(pf)))
        if filed == 'platform':
            return cls.db.search(cls.Q.platform.test(pf, args))
        return []


if __name__ == '__main__':
    for i in DBcore.search('platform', 'NS'):
        print i['title'].encode('utf-8')
