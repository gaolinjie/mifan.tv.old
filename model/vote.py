#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class VoteModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "vote"
        super(VoteModel, self).__init__()

    def add_new_vote(self, vote_info):
        return self.data(vote_info).add()

    def get_vote_by_topic_id_and_trigger_user_id(self, topic_id, trigger_user_id):
        where = "involved_topic_id = %s AND trigger_user_id = %s" % (topic_id, trigger_user_id)
        return self.where(where).find()

    def delete_vote_by_topic_id_and_trigger_user_id(self, topic_id, trigger_user_id):
    	where = "involved_topic_id = %s AND trigger_user_id = %s" % (topic_id, trigger_user_id)
        return self.where(where).delete()

    def get_up_vote_count_by_topic_id(self, topic_id):
        where = "involved_topic_id = %s AND status = 1" % topic_id
        return self.where(where).count()

    def get_down_vote_count_by_topic_id(self, topic_id):
        where = "involved_topic_id = %s AND status = -1" % topic_id
        return self.where(where).count()

    def update_vote_by_topic_id_and_trigger_user_id(self, topic_id, trigger_user_id, vote_info):
        where = "involved_topic_id = %s AND trigger_user_id = %s" % (topic_id, trigger_user_id)
        return self.where(where).data(vote_info).save()

    def get_vote_by_reply_id_and_trigger_user_id(self, reply_id, trigger_user_id):
        where = "involved_reply_id = %s AND trigger_user_id = %s" % (reply_id, trigger_user_id)
        return self.where(where).find()

    def delete_vote_by_reply_id_and_trigger_user_id(self, reply_id, trigger_user_id):
        where = "involved_reply_id = %s AND trigger_user_id = %s" % (reply_id, trigger_user_id)
        return self.where(where).delete()

    def update_vote_by_reply_id_and_trigger_user_id(self, reply_id, trigger_user_id, vote_info):
        where = "involved_reply_id = %s AND trigger_user_id = %s" % (reply_id, trigger_user_id)
        return self.where(where).data(vote_info).save()
