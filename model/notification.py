#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class NotificationModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "notification"
        super(NotificationModel, self).__init__()

    def add_new_notification(self, notification_info):
        return self.data(notification_info).add()

    def get_user_unread_notification_count(self, uid):
        where = "status = 0 AND involved_user_id = %s" % uid
        return self.where(where).count()

    def get_user_all_notifications(self, uid, num = 2, current_page = 1):
        where = "involved_user_id = %s" % uid
        join = "LEFT JOIN user AS trigger_user ON notification.trigger_user_id = trigger_user.uid \
                LEFT JOIN post AS involved_post ON notification.involved_post_id = involved_post.id \
                LEFT JOIN video AS involved_post_video ON involved_post.video_id = involved_post_video.id \
                LEFT JOIN topic AS involved_topic ON notification.involved_post_id = involved_topic.id \
                LEFT JOIN user AS involved_user ON notification.involved_user_id = involved_user.uid"
        order = "id DESC"
        field = "notification.*, \
                trigger_user.username as trigger_username, \
                trigger_user.avatar as trigger_avatar, \
                trigger_user.uid as trigger_uid, \
                involved_post_video.title as involved_post_video_title, \
                involved_topic.title as involved_topic_title, \
                involved_user.username as involved_username, \
                involved_user.avatar as involved_avatar"
        return self.where(where).join(join).field(field).order(order).pages(current_page = current_page, list_rows = num)

    def get_user_all_notifications_by_involved_type(self, uid, involved_type, num = 2, current_page = 1):
        where = "involved_user_id = %s AND (involved_type = %s OR involved_type = %s)" % (uid, involved_type, involved_type+2)
        join = "LEFT JOIN user AS trigger_user ON notification.trigger_user_id = trigger_user.uid \
                LEFT JOIN post AS involved_post ON notification.involved_post_id = involved_post.id \
                LEFT JOIN video AS involved_post_video ON involved_post.video_id = involved_post_video.id \
                LEFT JOIN topic AS involved_topic ON notification.involved_post_id = involved_topic.id \
                LEFT JOIN user AS involved_user ON notification.involved_user_id = involved_user.uid"
        order = "id DESC"
        field = "notification.*, \
                trigger_user.username as trigger_username, \
                trigger_user.avatar as trigger_avatar, \
                trigger_user.uid as trigger_uid, \
                involved_post_video.title as involved_post_video_title, \
                involved_topic.title as involved_topic_title, \
                involved_user.username as involved_username, \
                involved_user.avatar as involved_avatar"
        return self.where(where).join(join).field(field).order(order).pages(current_page = current_page, list_rows = num)

    def mark_user_unread_notification_as_read(self, uid):
        where = "status = 0 AND involved_user_id = %s" % uid
        return self.where(where).data({"status": 1}).save()

    def get_notification_by_notification_id(self, notification_id):
        where = "id = '%s'" % notification_id
        return self.where(where).find()

    def mark_notification_as_read_by_notification_id(self, notification_id):
        where = "id = '%s'" % notification_id
        return self.where(where).data({"status": 1}).save()

