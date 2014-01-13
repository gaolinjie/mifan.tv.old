#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class CommentModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "comment"
        super(CommentModel, self).__init__()

    def get_all_comments_by_post_id(self, post_id):
        where = "post_id = %s" % post_id
        join = "LEFT JOIN user ON comment.author_id = user.uid"
        order = "created ASC, id ASC"
        field = "comment.*, \
                user.username as author_username, \
                user.avatar as author_avatar"
        return self.where(where).order(order).join(join).field(field).select()

    def add_new_comment(self, comment_info):
        return self.data(comment_info).add()

