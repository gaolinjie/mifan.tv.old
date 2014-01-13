#!/usr/bin/env python
# coding=utf-8
#
## Copyright 2013 mifan.tv

import time
from lib.query import Query

class PlusModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "plus"
        super(PlusModel, self).__init__()

    def add_new_plus(self, plus_info):
        return self.data(plus_info).add()

    def get_plus_info_by_user_id_and_channel_id(self, user_id, channel_id):
        where = "user_id = %s AND object_id = %s" % (user_id, channel_id)
        return self.where(where).find()

    def delete_plus_info_by_user_id_and_channel_id(self, user_id, channel_id):
        where = "user_id = %s AND object_id = %s" % (user_id, channel_id)
        return self.where(where).delete()

    def get_user_plus_count(self, user_id):
        where = "user_id = %s" % user_id
        return self.where(where).count()

