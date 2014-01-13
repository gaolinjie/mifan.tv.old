#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 3n1b.com

import time
from lib.query import Query

class TopicModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "topic"
        super(TopicModel, self).__init__()

    def get_all_topics(self, num = 2, current_page = 1):
        join = "LEFT JOIN user AS author_user ON topic.author_id = author_user.uid \
                LEFT JOIN user AS last_replied_user ON topic.last_replied_by = last_replied_user.uid"
        order = "last_touched DESC, created DESC, last_replied_time DESC, id DESC"
        field = "topic.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                author_user.uid as author_uid, \
                last_replied_user.username as last_replied_username"
        return self.order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_all_topics_count(self):
        return self.count()

    def get_user_all_topics(self, uid, num = 32, current_page = 1):
        where = "topic.author_id = %s" % uid
        join = "LEFT JOIN user AS author_user ON topic.author_id = author_user.uid \
                LEFT JOIN user AS last_replied_user ON topic.last_replied_by = last_replied_user.uid"
        order = "id DESC"
        field = "topic.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                author_user.uid as author_uid, \
                last_replied_user.username as last_replied_username"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_user_all_topics_count(self, uid):
        where = "author_id = %s" % uid
        return self.where(where).count()

    def get_user_all_replied_topics(self, uid, num = 32, current_page = 1):
        where = "reply.uid = %s" % uid
        join = "LEFT JOIN reply ON topic.id = reply.tid LEFT JOIN user ON topic.uid = user.uid"
        order = "topic.id DESC"
        field = "*, topic.created as created"
        group = "tid"
        return self.where(where).order(order).join(join).field(field).group(group).pages(current_page = current_page, list_rows = num)

    def get_topic_by_topic_id(self, topic_id):
        where = "topic.id = %s" % topic_id
        join = "LEFT JOIN user AS author_user ON topic.author_id = author_user.uid \
                LEFT JOIN user AS last_replied_user ON topic.last_replied_by = last_replied_user.uid"
        field = "topic.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                author_user.uid as author_uid, \
                last_replied_user.username as last_replied_username"
        return self.where(where).join(join).field(field).find()

    def add_new_topic(self, topic_info):
        return self.data(topic_info).add()

    def update_topic_by_topic_id(self, topic_id, topic_info):
        where = "topic.id = %s" % topic_id
        return self.where(where).data(topic_info).save()

    def get_all_hot_topics(self):
        where = "topic.reply_count > 0"
        join = "LEFT JOIN user AS author_user ON topic.author_id = author_user.uid"
        order = "topic.reply_count DESC"
        field = "topic.*,\
                author_user.avatar as author_avatar"
        return self.where(where).join(join).order(order).field(field).limit(10).select()
