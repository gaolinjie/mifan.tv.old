#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class SubnavModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "subnav"
        super(SubnavModel, self).__init__()

    def get_all_subnavs(self):
        return self.select()

    def get_all_subnavs_count(self):
        return self.count()


    def get_subnav_by_subnav_id(self, subnav_id):
        where = "id = '%s'" % subnav_id
        return self.where(where).find()

    def get_subnav_by_subnav_name(self, subnav_name):
        where = "name = '%s'" % subnav_name
        return self.where(where).find()

    def get_subnav_by_subnav_title(self, subnav_title):
        where = "title = '%s'" % subnav_title
        return self.where(where).find()

    def get_subnavs_by_nav_id(self, nav_id):
        where = "subnav.nav_id = '%s'" % nav_id
        return self.where(where).select()

        

    