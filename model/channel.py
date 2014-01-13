#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class ChannelModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "channel"
        super(ChannelModel, self).__init__()

    def get_all_channels(self):
        return self.select()

    def get_all_channels_count(self):
        return self.count()

    def get_user_all_channels_count(self, uid):
        where = "author_id = %s" % uid
        return self.where(where).count()

    def get_channel_by_channel_id(self, channel_id):
        where = "id = '%s'" % channel_id
        join = "LEFT JOIN user AS author_user ON channel.author_id = author_user.uid"
        field = "channel.*, \
                author_user.username as author_username"
        return self.where(where).join(join).field(field).find()

    def get_channel_by_name(self, channel_name):
        where = "name = '%s'" % channel_name
        return self.where(where).find()

    def get_user_all_channels(self, user_id, num = 10, current_page = 1):
        where = "author_id = '%s'" % user_id
        join = "LEFT JOIN user AS author_user ON channel.author_id = author_user.uid \
                LEFT JOIN follow ON channel.id = follow.channel_id AND '%s' = follow.user_id" % user_id
        order = "channel.followers DESC, channel.created DESC, channel.id DESC"
        field = "channel.*, \
                author_user.username as author_username, \
                follow.user_id as follow_user_id"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_user_all_channels_by_nav_id(self, user_id, nav_id, num = 10, current_page = 1):
        where = "author_id = '%s' AND nav_id = '%s'" % (user_id, nav_id)
        join = "LEFT JOIN user AS author_user ON channel.author_id = author_user.uid \
                LEFT JOIN follow ON channel.id = follow.channel_id AND '%s' = follow.user_id" % user_id
        order = "channel.followers DESC, channel.created DESC, channel.id DESC"
        field = "channel.*, \
                author_user.username as author_username, \
                follow.user_id as follow_user_id"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_user_all_channels2(self, user_id):
        where = "author_id = '%s'" % user_id
        return self.where(where).select()

    def add_new_channel(self, channel_info):
        return self.data(channel_info).add()

    def get_channels_by_nav_id(self, nav_id, user_id, num = 6, current_page = 1):
        where = "channel.nav_id = %s" % nav_id
        join = "LEFT JOIN user AS author_user ON channel.author_id = author_user.uid \
                LEFT JOIN follow ON channel.id = follow.channel_id AND '%s' = follow.user_id" % user_id
        order = "channel.created DESC, channel.id DESC"
        field = "channel.*, \
                author_user.username as author_username, \
                follow.user_id as follow_user_id"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)
    
    def get_channels_by_nav_id_and_subnav_id(self, nav_id, user_id, subnav_id, num = 6, current_page = 1):
        where = "channel.nav_id = %s AND channel.subnav_id = %s" % (nav_id, subnav_id)
        join = "LEFT JOIN user AS author_user ON channel.author_id = author_user.uid \
                LEFT JOIN follow ON channel.id = follow.channel_id AND '%s' = follow.user_id" % user_id
        order = "channel.created DESC, channel.id DESC"
        field = "channel.*, \
                author_user.username as author_username, \
                follow.user_id as follow_user_id"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def update_channel_info_by_channel_id(self, channel_id, channel_info):
        where = "channel.id = %s" % channel_id
        return self.where(where).data(channel_info).save()

    def set_channel_avatar_by_channel_id(self, channel_id, avatar_name):
        where = "id = %s" % channel_id
        return self.data({
            "avatar": avatar_name
        }).where(where).save()

    def set_channel_cover_by_channel_id(self, channel_id, cover_name):
        where = "id = %s" % channel_id
        return self.data({
            "cover": cover_name
        }).where(where).save()

    
    def get_user_other_channels(self, user_id, channel_id, num = 3, current_page = 1):
        where = "channel.author_id = %s AND channel.id <> %s" % (user_id, channel_id)
        join = "LEFT JOIN user AS author_user ON channel.author_id = author_user.uid \
                LEFT JOIN follow ON channel.id = follow.channel_id AND '%s' = follow.user_id" % user_id
        order = "channel.created DESC, channel.id DESC"
        field = "channel.*, \
                author_user.username as author_username, \
                follow.user_id as follow_user_id"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)


    def get_hot_channels(self, user_id, num = 10, current_page = 1):
        join = "LEFT JOIN user AS author_user ON channel.author_id = author_user.uid \
                LEFT JOIN follow ON channel.id = follow.channel_id AND '%s' = follow.user_id" % user_id
        order = "channel.followers DESC, channel.created DESC, channel.id DESC"
        field = "channel.*, \
                author_user.username as author_username, \
                follow.user_id as follow_user_id"
        return self.order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_hot_channels_by_nav_id(self, user_id, nav_id, num = 10, current_page = 1):
        where = "nav_id = '%s'" % nav_id
        join = "LEFT JOIN user AS author_user ON channel.author_id = author_user.uid \
                LEFT JOIN follow ON channel.id = follow.channel_id AND '%s' = follow.user_id" % user_id
        order = "channel.followers DESC, channel.created DESC, channel.id DESC"
        field = "channel.*, \
                author_user.username as author_username, \
                follow.user_id as follow_user_id"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)