#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class FavoriteModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "favorite"
        super(FavoriteModel, self).__init__()

    def add_new_favorite(self, favorite_info):
        return self.data(favorite_info).add()

    def delete_favorite_info_by_user_id_and_post_id(self, user_id, post_id):
        where = "user_id = %s AND post_id = %s" % (user_id, post_id)
        return self.where(where).delete()

    def delete_favorite_by_post_id(self, post_id):
        where = "post_id = %s" % post_id
        return self.where(where).delete()

    def get_favorite_by_post_id_and_user_id(self, user_id, post_id):
        where = "post_id = %s AND user_id = %s" % (post_id, user_id)
        return self.where(where).find()

    def get_user_favorite_count(self, user_id):
        where = "user_id = %s" % user_id
        return self.where(where).count()

    def get_user_all_favorites(self, user_id, num = 3, current_page = 1):
        where = "favorite.user_id = %s" % user_id
        join = "LEFT JOIN post ON favorite.post_id = post.id \
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid \
                LEFT JOIN channel ON post.channel_id = channel.id \
                LEFT JOIN video ON post.video_id = video.id \
                LEFT JOIN nav ON channel.nav_id = nav.id \
                LEFT JOIN comment ON post.last_comment = comment.id \
                LEFT JOIN user AS comment_user ON comment.author_id = comment_user.uid \
                LEFT JOIN later ON '%s' = later.user_id AND post.id = later.post_id" % user_id
        order = "favorite.created DESC, favorite.id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                channel.id as channel_id, \
                channel.name as channel_name, \
                nav.name as nav_name, \
                nav.title as nav_title, \
                video.source as video_source, \
                video.flash as video_flash, \
                video.title as video_title, \
                video.thumb as video_thumb, \
                video.link as video_link, \
                comment.content as comment_content, \
                comment.created as comment_created, \
                comment_user.username as comment_user_name, \
                comment_user.avatar as comment_user_avatar, \
                later.id as later_id"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_user_all_favorite_posts_by_nav_id(self, user_id, nav_id, num = 16, current_page = 1):
        where = "favorite.user_id = %s AND '%s' = favorite.nav_id" % (user_id, nav_id)
        join = "LEFT JOIN post ON favorite.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid \
                LEFT JOIN channel ON post.channel_id = channel.id \
                LEFT JOIN video ON post.video_id = video.id \
                LEFT JOIN nav ON channel.nav_id = nav.id \
                LEFT JOIN comment ON post.last_comment = comment.id \
                LEFT JOIN user AS comment_user ON comment.author_id = comment_user.uid \
                LEFT JOIN later ON '%s' = later.user_id AND post.id = later.post_id" % user_id
        order = "favorite.created DESC, favorite.id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                channel.id as channel_id, \
                channel.name as channel_name, \
                nav.name as nav_name, \
                nav.title as nav_title, \
                video.source as video_source, \
                video.flash as video_flash, \
                video.title as video_title, \
                video.thumb as video_thumb, \
                video.link as video_link, \
                comment.content as comment_content, \
                comment.created as comment_created, \
                comment_user.username as comment_user_name, \
                comment_user.avatar as comment_user_avatar, \
                later.id as later_id"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)