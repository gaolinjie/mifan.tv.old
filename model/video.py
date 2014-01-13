#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class VideoModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "video"
        super(VideoModel, self).__init__()

    def add_new_video(self, video_info):
        return self.data(video_info).add()


