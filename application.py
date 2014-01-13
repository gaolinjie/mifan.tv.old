#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

# cat /etc/mime.types
# application/octet-stream    crx

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os.path
import re
import memcache
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


import handler.topic
import handler.user
import handler.channel

from tornado.options import define, options
from lib.loader import Loader
from lib.session import Session, SessionManager
from jinja2 import Environment, FileSystemLoader

define("port", default = 80, help = "run on the given port", type = int)
define("mysql_host", default = "localhost", help = "community database host")
define("mysql_database", default = "mifan", help = "community database name")
define("mysql_user", default = "mifan", help = "community database user")
define("mysql_password", default = "mifan", help = "community database password")

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            blog_title = u"mifan.tv",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = False,
            cookie_secret = "cookie_secret_code",
            login_url = "/login",
            autoescape = None,
            jinja2 = Environment(loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")), trim_blocks = True),
            reserved = ["user", "topic", "home", "setting", "forgot", "login", "logout", "register", "admin"],
            debug=True,
        )

        handlers = [
            (r"/", handler.topic.IndexHandler),
            (r"/video", handler.channel.VideoHandler),
            (r"/favorite", handler.topic.FavoriteHandler),
            (r"/later", handler.topic.LaterHandler),
            (r"/later/clear", handler.topic.LaterClearHandler),
            (r"/watch", handler.topic.WatchHandler),
            (r"/watch/clear", handler.topic.WatchClearHandler),
            (r"/follow", handler.channel.FollowsHandler),
            (r"/notification", handler.topic.NotificationsHandler),
            (r"/n/(\d+)", handler.topic.NotificationHandler),
            (r"/c/(\d+)", handler.channel.ChannelHandler),
            (r"/u/(.*)", handler.topic.UserHandler),
            (r"/channels/u/(.*)", handler.channel.UserOtherChannelsHandler),
            (r"/login", handler.user.LoginHandler),
            (r"/logout", handler.user.LogoutHandler),
            (r"/signup", handler.user.RegisterHandler),
            (r"/forgot", handler.user.ForgotPasswordHandler),
            (r"/f/(\d+)", handler.channel.FollowHandler),
            (r"/p/(\d+)", handler.topic.PostHandler),
            (r"/s/(\d+)", handler.topic.SpamPostHandle),
            (r"/d/(\d+)", handler.topic.DeletePostHandle),
            (r"/comment/(\d+)", handler.topic.CommentHandler),
            (r"/rate/(\d+)", handler.topic.RateHandler),
            (r"/setting", handler.user.SettingHandler),
            (r"/setting/avatar", handler.user.SettingAvatarHandler),
            (r"/setting/cover", handler.user.SettingCoverHandler),
            (r"/setting/password", handler.user.SettingPasswordHandler),
            (r"/c/(\d+)/setting", handler.channel.ChannelSettingHandler),
            (r"/c/(\d+)/setting/avatar", handler.channel.ChannelSettingAvatarHandler),
            (r"/c/(\d+)/setting/cover", handler.channel.ChannelSettingCoverHandler),
            (r"/micro", handler.channel.MicroHandler),
            (r"/movie", handler.channel.MovieHandler),
            (r"/tv", handler.channel.TVHandler),
            (r"/star", handler.channel.StarHandler),
            (r"/favorite/(\d+)", handler.topic.FavoriteManagerHandler),
            (r"/later/(\d+)", handler.topic.LaterManagerHandler),
            (r"/watch/(\d+)", handler.topic.WatchManagerHandler),
            (r"/suggestions", handler.channel.SuggestionsHandler),
            (r"/hot", handler.channel.HotChannelsHandler),
            (r"/searchchannel", handler.channel.SearchChannelHandler),

            (r"/forum", handler.topic.ForumHandler),
            (r"/t/create", handler.topic.CreateTopicHandler),
            (r"/t/(\d+)", handler.topic.ViewHandler),
            (r"/t/edit/(.*)", handler.topic.EditHandler),
            (r"/reply/edit/(.*)", handler.topic.ReplyEditHandler),

            (r"/(favicon\.ico)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(sitemap.*$)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(bdsitemap\.txt)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(orca\.txt)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = torndb.Connection(
            host = options.mysql_host, database = options.mysql_database,
            user = options.mysql_user, password = options.mysql_password
        )

        # Have one global loader for loading models and handles
        self.loader = Loader(self.db)

        # Have one global model for db query
        self.user_model = self.loader.use("user.model")
        self.follow_model = self.loader.use("follow.model")
        self.post_model = self.loader.use("post.model")
        self.channel_model = self.loader.use("channel.model")
        self.plus_model = self.loader.use("plus.model")
        self.comment_model = self.loader.use("comment.model")
        self.nav_model = self.loader.use("nav.model")
        self.subnav_model = self.loader.use("subnav.model")
        self.video_model = self.loader.use("video.model")
        self.favorite_model = self.loader.use("favorite.model")
        self.later_model = self.loader.use("later.model")
        self.watch_model = self.loader.use("watch.model")
        self.rate_model = self.loader.use("rate.model")
        self.notification_model = self.loader.use("notification.model")

        self.topic_model = self.loader.use("topic.model")
        self.reply_model = self.loader.use("reply.model")

        # Have one global session controller
        self.session_manager = SessionManager(settings["cookie_secret"], ["127.0.0.1:11211"], 0)

        # Have one global memcache controller
        self.mc = memcache.Client(["127.0.0.1:11211"])

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

