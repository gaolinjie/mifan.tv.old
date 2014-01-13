#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class NavModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "nav"
        super(NavModel, self).__init__()

    def get_all_navs(self):
        return self.select()

    def get_all_navs_count(self):
        return self.count()


    def get_nav_by_nav_id(self, nav_id):
        where = "id = '%s'" % nav_id
        return self.where(where).find()

    def get_nav_by_nav_name(self, nav_name):
        where = "name = '%s'" % nav_name
        return self.where(where).find()

    def get_nav_by_nav_title(self, nav_title):
        where = "title = '%s'" % nav_title
        return self.where(where).find()