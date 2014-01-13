#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class RateModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "rate"
        super(RateModel, self).__init__()

    def add_new_rate(self, rate_info):
        return self.data(rate_info).add()

    def delete_rate_info_by_user_id_and_post_id(self, user_id, post_id):
        where = "user_id = %s AND post_id = %s" % (user_id, post_id)
        return self.where(where).delete()

    def get_rate_by_post_id_and_user_id(self, user_id, post_id):
        where = "post_id = %s AND user_id = %s" % (post_id, user_id)
        return self.where(where).find()

    def get_user_rate_count(self, user_id):
        where = "user_id = %s" % user_id
        return self.where(where).count()
