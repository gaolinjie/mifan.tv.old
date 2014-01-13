#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import uuid
import hashlib
import Image
import StringIO
import time
import json
import re
import urllib2
import tornado.web
import lib.jsonp
import pprint
import math
import datetime 

from base import *
from lib.variables import *
from form.topic import *
from lib.variables import gen_random
from lib.xss import XssCleaner
from lib.utils import find_mentions
from lib.reddit import hot
from lib.utils import pretty_date

from lib.utils import find_video_id_from_url

class IndexHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["navs"] = self.nav_model.get_all_navs()
        if(user_info):           
            template_variables["channels"] = self.channel_model.get_user_all_channels2(user_id = user_info["uid"])
            template_variables["maylike_channels"] = self.channel_model.get_hot_channels(user_info["uid"], num=20)
               
            if(tab=="all"):
                notice_text = "你还未关注任何频道呢，先去各视频板块关注你感兴趣的频道吧~~"
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.follow_model.get_user_all_follow_posts(user_id = user_info["uid"], current_page = page)
            else:
                nav_id=1
                if (tab=="video"):
                    nav_id=1
                    notice_text = "你还未关注任何短片频道呢，先去各短片板块关注你感兴趣的频道吧~~"
                if (tab=="micro"):
                    nav_id=2
                    notice_text = "你还未关注任何微电影频道呢，先去微电影板块关注你感兴趣的频道吧~~"
                if (tab=="movie"):
                    nav_id=3
                    notice_text = "你还未关注任何电影频道呢，先去电影板块关注你感兴趣的频道吧~~"
                if (tab=="star"):
                    nav_id=4
                    notice_text = "你还未关注任何明星频道呢，先去明星板块关注你感兴趣的频道吧~~"
                template_variables["active_tab"] = tab           
                template_variables["posts"] = self.follow_model.get_user_all_follow_posts_by_nav_id(user_id = user_info["uid"], nav_id = nav_id, current_page = page)           
            template_variables["notice_text"] = notice_text
        else:
            template_variables["channels"] = self.channel_model.get_all_channels()
            template_variables["maylike_channels"] = self.channel_model.get_hot_channels(0, num=20)
               
            if(tab=="all"):
                notice_text = "你还未关注任何频道呢，先去各视频板块关注你感兴趣的频道吧~~"
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.post_model.get_all_posts(current_page = page)
            else:
                nav_id=1
                if (tab=="video"):
                    nav_id=1
                    notice_text = "你还未关注任何短片频道呢，先去各短片板块关注你感兴趣的频道吧~~"
                if (tab=="micro"):
                    nav_id=2
                    notice_text = "你还未关注任何微电影频道呢，先去微电影板块关注你感兴趣的频道吧~~"
                if (tab=="movie"):
                    nav_id=3
                    notice_text = "你还未关注任何电影频道呢，先去电影板块关注你感兴趣的频道吧~~"
                if (tab=="star"):
                    nav_id=4
                    notice_text = "你还未关注任何明星频道呢，先去明星板块关注你感兴趣的频道吧~~"
                template_variables["active_tab"] = tab           
                template_variables["posts"] = self.post_model.get_all_posts_by_nav_id(nav_id = nav_id, current_page = page)           
            template_variables["notice_text"] = notice_text

        self.render("index.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        tab = self.get_argument('tab', "post")
        template_variables = {}
        user_info = self.current_user

        if (tab=="post"):
            # validate the fields
            form = PostForm(self)

            if not form.validate():
                self.get({"errors": form.errors})
                return

            # continue while validate succeed

            video_link = form.link.data
            video_id = find_video_id_from_url(video_link)
            json_link = "http://v.youku.com/player/getPlayList/VideoIDS/"+video_id+"/timezone/+08/version/5/source/out?password=&ran=2513&n=3"
            video_json = json.load(urllib2.urlopen(json_link))
            video_logo = video_json[u'data'][0][u'logo']
            video_title = video_json[u'data'][0][u'title']
            video_flash = "http://player.youku.com/player.php/sid/"+video_id+"/v.swf"
            print video_title

            video_info = {
                "source": "youku",
                "flash": video_flash,
                "link": video_link,
                "title": video_title,
                "thumb": video_logo,
            }
            vid = self.video_model.add_new_video(video_info)

            channel_name = form.channel.data
            channel = self.channel_model.get_channel_by_name(channel_name = channel_name)
        
            post_info = {
                "author_id": self.current_user["uid"],
                "channel_id": channel["id"],
                "nav_id": channel["nav_id"],
                "video_id": vid,
                "intro": form.intro.data,
                "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            }

            post_id = self.post_model.add_new_post(post_info)

            self.channel_model.update_channel_info_by_channel_id(channel.id, {"plus":channel.plus+3, "posts": channel.posts+1})
            self.user_model.update_user_info_by_user_id(user_info["uid"], {"plus":user_info["plus"]+3})

            # create @username follow
            for username in set(find_mentions(form.intro.data)):
                print username
                mentioned_user = self.user_model.get_user_by_username(username)

                if not mentioned_user:
                    continue

                if mentioned_user["uid"] == self.current_user["uid"]:
                    continue

                if mentioned_user["uid"] == post_info["author_id"]:
                    continue

                self.follow_model.add_new_follow({
                    "user_id": mentioned_user.uid,
                    "post_id": post_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                })

            self.redirect("/")
        else:
            form = ChannelForm2(self)

            if not form.validate():
                self.get({"errors": form.errors})
                return

            nav = self.nav_model.get_nav_by_nav_title(form.nav.data)
            channel_info = {
                "name": form.name.data,
                "intro": form.intro.data,
                "nav_id": nav["id"],
                "plus": 0,
                "followers": 0,
                "posts": 0,
                "author_id": self.current_user["uid"],
                "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            self.channel_model.add_new_channel(channel_info)

            channel = self.channel_model.get_channel_by_name(channel_name = channel_info["name"])

            follow_info = {
                "user_id": self.current_user["uid"],
                "channel_id": channel["id"],
                "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            self.follow_model.add_new_follow(follow_info)

            self.redirect("/c/"+str(channel["id"]))

class FavoriteHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels(user_id = user_info["uid"])
            
            if(tab=="all"):
                notice_text = "你还没收藏任何视频"
                template_variables["active_nav"] = "favorite"
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.favorite_model.get_user_all_favorites(user_id = user_info["uid"], current_page = page)           
            else:
                print tab
                if (tab=="video"):
                    notice_text = "你还没收藏任何短片"
                    nav_id=1
                if (tab=="micro"):
                    notice_text = "你还没收藏任何微电影"
                    nav_id=2
                if (tab=="movie"):
                    notice_text = "你还没收藏任何电影"
                    nav_id=3
                if (tab=="star"):
                    notice_text = "你还没收藏任何明星视频"
                    nav_id=4
                template_variables["active_tab"] = tab
                template_variables["posts"] = self.favorite_model.get_user_all_favorite_posts_by_nav_id(user_id = user_info["uid"], nav_id = nav_id, current_page = page)           
            template_variables["notice_text"] = notice_text        
        else:
            self.redirect("/login")

        self.render("favorite.html", **template_variables)

class LaterHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels(user_id = user_info["uid"])
            
            if(tab=="all"):
                notice_text = "还没有视频被你加入稍后观看队列"
                template_variables["active_nav"] = "later"
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.later_model.get_user_all_laters(user_id = user_info["uid"], current_page = page)           
            else:
                if (tab=="video"):
                    notice_text = "还没有短片被你加入稍后观看队列"
                    nav_id=1
                if (tab=="micro"):
                    notice_text = "还没有微电影被你加入稍后观看队列"
                    nav_id=2
                if (tab=="movie"):
                    notice_text = "还没有电影被你加入稍后观看队列"
                    nav_id=3
                if (tab=="star"):
                    notice_text = "还没有明星视频被你加入稍后观看队列"
                    nav_id=4
                template_variables["active_tab"] = tab
                template_variables["posts"] = self.later_model.get_user_all_later_posts_by_nav_id(user_id = user_info["uid"], nav_id = nav_id, current_page = page)           
            template_variables["notice_text"] = notice_text  
        else:
            self.redirect("/login")

        self.render("later.html", **template_variables)


class WatchHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels(user_id = user_info["uid"])
            
            if(tab=="all"):
                notice_text = "你还没看过任何视频"
                template_variables["active_nav"] = "watch"
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.watch_model.get_user_all_watchs(user_id = user_info["uid"], current_page = page)           
            else:
                if (tab=="video"):
                    notice_text = "你还没看过任何短片"
                    nav_id=1
                if (tab=="micro"):
                    notice_text = "你还没看过任何微电影"
                    nav_id=2
                if (tab=="movie"):
                    notice_text = "你还没看过任何电影"
                    nav_id=3
                if (tab=="star"):
                    notice_text = "你还没看过任何明星视频"
                    nav_id=4
                template_variables["active_tab"] = tab
                template_variables["posts"] = self.watch_model.get_user_all_watch_posts_by_nav_id(user_id = user_info["uid"], nav_id = nav_id, current_page = page)           
            template_variables["notice_text"] = notice_text  
        else:
            self.redirect("/login")

        self.render("watch.html", **template_variables)


class NotificationsHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random

        if(user_info):
            template_variables["active_nav"] = "notification"
            template_variables["active_tab"] = tab
            if (tab=="all"):
                template_variables["notifications"] = self.notification_model.get_user_all_notifications(user_info["uid"], current_page = page)
            elif (tab=="comment"):
                template_variables["notifications"] = self.notification_model.get_user_all_notifications_by_involved_type(user_info["uid"], 1, current_page = page)
            elif (tab=="mention"):
                template_variables["notifications"] = self.notification_model.get_user_all_notifications_by_involved_type(user_info["uid"], 0, current_page = page)
            elif (tab=="allread"):
                self.notification_model.mark_user_unread_notification_as_read(user_info["uid"])
                self.redirect("/notification")
            notice_text = "暂时还没有消息"
            if (tab == "comment"):
                notice_text = "暂时还没有回复"
            if (tab == "mention"):
                notice_text = "暂时还没有人提到你"
            template_variables["notice_text"] = notice_text
        else:
            self.redirect("/login")

        self.render("notification.html", **template_variables)


class NotificationHandler(BaseHandler):
    def get(self, notification_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            notification = self.notification_model.get_notification_by_notification_id(notification_id = notification_id)
            self.notification_model.mark_notification_as_read_by_notification_id(notification_id = notification_id)
            if notification.involved_type < 2:
                self.redirect("/p/"+str(notification.involved_post_id))
            else:
                self.redirect("/t/"+str(notification.involved_post_id))
        else:
            self.redirect("/login")



class UserHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random    
        page = int(self.get_argument("page", "1"))
        
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels2(user_id = user_info["uid"])
            
            if(re.match(r'^\d+$', user)):
                view_user_info = self.user_model.get_user_by_uid(user)
            else:
                view_user_info = self.user_model.get_user_by_username(user)
            template_variables["user_all_channels_count"] = self.channel_model.get_user_all_channels_count(view_user_info["uid"])
            template_variables["user_all_channels"] = self.channel_model.get_user_all_channels(view_user_info["uid"], num=3, current_page = page)
            template_variables["view_user_info"] = view_user_info
            template_variables["posts"] = self.post_model.get_user_all_posts(current_page = page, user_id = view_user_info["uid"])
        else:
            self.redirect("/login")

        self.render("user/user.html", **template_variables)


class PlusChannelHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            channle = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
            plus = self.plus_model.get_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(plus):
                self.plus_model.delete_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
                self.channel_model.update_channel_info_by_channel_id(channel_id, {"plus": channle.plus-1,})
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_plused",
                }))
            else:
                print "fasdfasd"
                plus_info = {
                    "type": "channel",
                    "user_id": user_info["uid"],
                    "object_id": channel_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.plus_model.add_new_plus(plus_info)
                self.channel_model.update_channel_info_by_channel_id(channel_id, {"plus": channle.plus+1,})
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_plused",
                }))

class CommentHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            comments = self.comment_model.get_all_comments_by_post_id(post_id)

            jarray = []
            i = 0
            for comment in comments:
                jobject = {
                    "content": comment.content,
                    "author_username": comment.author_username,
                    "author_avatar": comment.author_avatar,
                    "created": pretty_date(comment.created)
                }
                jarray.append(jobject)
                i=i+1

            self.write(lib.jsonp.print_JSON({"comments": jarray}))

    @tornado.web.authenticated
    def post(self, post_id, template_variables = {}):
        user_info = self.current_user

        data = json.loads(self.request.body)
        comment_content = data["comment_content"]

        if(user_info):
            comment_info = {
                "author_id": user_info["uid"],
                "post_id": post_id,
                "content": comment_content,
                "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            comment_id = self.comment_model.add_new_comment(comment_info)

            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            self.post_model.update_post_by_post_id(post_id, {"last_comment": comment_id, 
                                                            "comment_count": post.comment_count+1,})
            self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "successed",
            }))

            # create reply notification
            if not self.current_user["uid"] == post.author_id:
                self.notification_model.add_new_notification({
                    "trigger_user_id": self.current_user["uid"],
                    "involved_type": 1, # 0: mention, 1: reply
                    "involved_user_id": post.author_id,
                    "involved_post_id": post.id,
                    "involved_comment_id": comment_id,
                    "content": comment_content,
                    "status": 0,
                    "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                })

            # create @username notification
            for username in set(find_mentions(comment_content)):
                print username
                mentioned_user = self.user_model.get_user_by_username(username)

                if not mentioned_user:
                    continue

                if mentioned_user["uid"] == self.current_user["uid"]:
                    continue

                if mentioned_user["uid"] == post.author_id:
                    continue

                self.notification_model.add_new_notification({
                    "trigger_user_id": self.current_user["uid"],
                    "involved_type": 0, # 0: mention, 1: reply
                    "involved_user_id": mentioned_user["uid"],
                    "involved_post_id": post.id,
                    "involved_comment_id": comment_id,
                    "content": comment_content,
                    "status": 0,
                    "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                })

            channel = self.channel_model.get_channel_by_channel_id(channel_id = post.channel_id)
            self.channel_model.update_channel_info_by_channel_id(channel.id, {"plus":channel.plus+1})
            user = self.user_model.get_user_by_uid(post.author_id)
            self.user_model.update_user_info_by_user_id(user.uid, {"plus":user.plus+1})
        else:
            self.write(lib.jsonp.print_JSON({
                    "success": 0,
                    "message": "failed",
            }))

class RateHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self, post_id, template_variables = {}):
        print "fdasfas"
        user_info = self.current_user

        data = json.loads(self.request.body)
        print data["score"]
        score = data["score"]*2

        if(user_info):
            rate = self.rate_model.get_rate_by_post_id_and_user_id(user_info["uid"], post_id)
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            if(rate):
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "rated",
                }))
            else:
                total_score = post.score * post.votes + score
                final_score = total_score / (post.votes+1)
                post_info = {
                    "score": final_score,
                    "votes": post.votes+1,
                }
                self.post_model.update_post_by_post_id(post_id, post_info)
                rate_info = {
                    "user_id": user_info["uid"],
                    "post_id": post_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.rate_model.add_new_rate(rate_info)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "successed",
                }))

                channel = self.channel_model.get_channel_by_channel_id(channel_id = post.channel_id)
                self.channel_model.update_channel_info_by_channel_id(channel.id, {"plus":channel.plus+data["score"]-3})
                user = self.user_model.get_user_by_uid(post.author_id)
                self.user_model.update_user_info_by_user_id(user.uid, {"plus":user.plus+data["score"]-3})
        else:
            self.write(lib.jsonp.print_JSON({
                    "success": 0,
                    "message": "failed",
                }))

class FavoriteManagerHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            favorite = self.favorite_model.get_favorite_by_post_id_and_user_id(user_info["uid"], post_id)
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            if(favorite):
                self.favorite_model.delete_favorite_info_by_user_id_and_post_id(user_info["uid"], post_id)
                self.post_model.update_post_by_post_id(post_id, {"favorite": post.favorite-1})
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_favorited",
                }))
                channel = self.channel_model.get_channel_by_channel_id(channel_id = post.channel_id)
                self.channel_model.update_channel_info_by_channel_id(channel.id, {"plus":channel.plus-2})
                user = self.user_model.get_user_by_uid(post.author_id)
                self.user_model.update_user_info_by_user_id(user.uid, {"plus":user.plus-2})
            else:
                favorite_info = {
                    "user_id": user_info["uid"],
                    "post_id": post_id,
                    "nav_id": post.nav_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.favorite_model.add_new_favorite(favorite_info)
                self.post_model.update_post_by_post_id(post_id, {"favorite": post.favorite+1})
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_favorited",
                }))
                channel = self.channel_model.get_channel_by_channel_id(channel_id = post.channel_id)
                self.channel_model.update_channel_info_by_channel_id(channel.id, {"plus":channel.plus+2})
                user = self.user_model.get_user_by_uid(post.author_id)
                self.user_model.update_user_info_by_user_id(user.uid, {"plus":user.plus+2})

class LaterManagerHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            later = self.later_model.get_later_by_post_id_and_user_id(user_info["uid"], post_id)
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            if(later):
                self.later_model.delete_later_info_by_user_id_and_post_id(user_info["uid"], post_id)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_latered",
                }))
            else:
                later_info = {
                    "user_id": user_info["uid"],
                    "post_id": post_id,
                    "nav_id": post.nav_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.later_model.add_new_later(later_info)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_latered",
                }))

class DeletePostHandle(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            if(post):
                self.post_model.delete_post_by_post_id(post_id)
                self.favorite_model.delete_favorite_by_post_id(post_id)
                self.later_model.delete_later_by_post_id(post_id)
                self.watch_model.delete_watch_by_post_id(post_id)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "post_deleted",
                }))

            else:
                self.write(lib.jsonp.print_JSON({
                    "success": 0,
                    "message": "post_unfound",
                }))

class SpamPostHandle(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            if(post):
                self.post_model.update_post_by_post_id(post_id, {"spam": post.spam+1})

                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "post_spamed",
                }))

            else:
                self.write(lib.jsonp.print_JSON({
                    "success": 0,
                    "message": "post_unfound",
                }))

class WatchManagerHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            watch = self.watch_model.get_watch_by_post_id_and_user_id(user_info["uid"], post_id)
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            if(not watch):
                watch_info = {
                    "user_id": user_info["uid"],
                    "post_id": post_id,
                    "nav_id": post.nav_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.watch_model.add_new_watch(watch_info)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_watched",
                }))

class LaterClearHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            later = self.later_model.delete_user_all_laters(user_info["uid"])
            self.redirect("/later")

class WatchClearHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            later = self.watch_model.delete_user_all_watchs(user_info["uid"])
            self.redirect("/watch")
            

class PostHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):  
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)        
            template_variables["post"] = post
            template_variables["comments"] = self.comment_model.get_all_comments_by_post_id(post_id)

            watch = self.watch_model.get_watch_by_post_id_and_user_id(user_info["uid"], post_id) 
            if(not watch):
                print "fasfasdfsad"
                watch_info = {
                    "user_id": user_info["uid"],
                    "post_id": post_id,
                    "nav_id": post.nav_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.watch_model.add_new_watch(watch_info)
        else:
            self.redirect("/login")

        self.render("post.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        self.redirect("/")




class ForumHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["active_page"] = "forum"
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["topics"] = self.topic_model.get_all_topics(current_page = page)           
        else:
            self.redirect("/login")        
        template_variables["gen_random"] = gen_random    
        notice_text = "暂时还没有话题，发出您的讨论吧。"
        template_variables["notice_text"] = notice_text
        self.render("topics.html", **template_variables)


class CreateTopicHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, node = None, template_variables = {}):
        user_info = self.current_user
        template_variables["active_page"] = "forum"
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        self.render("topic/create.html", **template_variables)

    @tornado.web.authenticated
    def post(self, node = None, template_variables = {}):
        print "CreateHandler:post"
        template_variables = {}

        # validate the fields
        form = CreateForm(self)

        if not form.validate():
            self.get(node_slug, {"errors": form.errors})
            return

        # continue while validate succeed     
        topic_info = {
            "author_id": self.current_user["uid"],
            "title": form.title.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "node_id": 0,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            "reply_count": 0,
            "last_touched": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        topic_id = self.topic_model.add_new_topic(topic_info)

        # create @username notification

        for username in set(find_mentions(form.content.data)):
            mentioned_user = self.user_model.get_user_by_username(username)

            if not mentioned_user:
                continue

            if mentioned_user["uid"] == self.current_user["uid"]:
                continue

            if mentioned_user["uid"] == topic_info["author_id"]:
                continue

            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 2, # 0: mention, 1: comment, 2: topic mention, 3: topic reply
                "involved_user_id": mentioned_user["uid"],
                "involved_post_id": topic_id,
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        self.redirect("/forum")

class ViewHandler(BaseHandler):
    def get(self, topic_id, template_variables = {}):
        user_info = self.current_user
        template_variables["active_page"] = "forum"
        page = int(self.get_argument("page", "1"))
        user_info = self.get_current_user()
        template_variables["user_info"] = user_info

        template_variables["gen_random"] = gen_random
        template_variables["topic"] = self.topic_model.get_topic_by_topic_id(topic_id)

        # check reply count and cal current_page if `p` not given
        reply_num = 16
        reply_count = template_variables["topic"]["reply_count"]
        reply_last_page = (reply_count / reply_num + (reply_count % reply_num and 1)) or 1
        page = int(self.get_argument("page", reply_last_page))
        template_variables["reply_num"] = reply_num
        template_variables["current_page"] = page

        template_variables["replies"] = self.reply_model.get_all_replies_by_topic_id(topic_id, user_info["uid"], current_page = page)

        # update topic reply_count and hits

        self.topic_model.update_topic_by_topic_id(topic_id, {
            "reply_count": template_variables["replies"]["page"]["total"],
            "hits": (template_variables["topic"]["hits"] or 0) + 1,
        })

        self.render("topic/view.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = ReplyForm(self)

        if not form.validate():
            self.get(form.tid.data, {"errors": form.errors})
            return

        # continue while validate succeed

        topic_info = self.topic_model.get_topic_by_topic_id(form.tid.data)
        replied_info = self.reply_model.get_user_reply_by_topic_id(self.current_user["uid"], form.tid.data)

        if(not topic_info):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_topic_info"] = [u"要回复的帖子不存在"]
            self.get(template_variables)
            return

        reply_info = {
            "author_id": self.current_user["uid"],
            "topic_id": form.tid.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        reply_id = self.reply_model.add_new_reply(reply_info)

        # update topic last_replied_by and last_replied_time

        self.topic_model.update_topic_by_topic_id(form.tid.data, {
            "last_replied_by": self.current_user["uid"],
            "last_replied_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "last_touched": time.strftime('%Y-%m-%d %H:%M:%S'),
        })

        # create reply notification

        if not self.current_user["uid"] == topic_info["author_id"]:
            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 3, # 0: mention, 1: comment, 2: topic mention, 3: topic reply
                "involved_user_id": topic_info["author_id"],
                "involved_post_id": form.tid.data,
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # create @username notification

        for username in set(find_mentions(form.content.data)):
            print username
            mentioned_user = self.user_model.get_user_by_username(username)

            if not mentioned_user:
                continue

            if mentioned_user["uid"] == self.current_user["uid"]:
                continue

            if mentioned_user["uid"] == topic_info["author_id"]:
                continue

            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 2, # 0: mention, 1: comment, 2: topic mention, 3: topic reply
                "involved_user_id": mentioned_user["uid"],
                "involved_post_id": form.tid.data,
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # self.get(form.tid.data)
        self.redirect("/t/%s#reply%s" % (form.tid.data, topic_info["reply_count"] + 1))

class EditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, topic_id, template_variables = {}):
        user_info = self.current_user
        template_variables["active_page"] = "forum"
        template_variables["user_info"] = user_info
        template_variables["topic"] = self.topic_model.get_topic_by_topic_id(topic_id)
        template_variables["gen_random"] = gen_random
        self.render("topic/edit.html", **template_variables)

    @tornado.web.authenticated
    def post(self, topic_id, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = CreateForm(self)

        if not form.validate():
            self.get(topic_id, {"errors": form.errors})
            return

        # continue while validate succeed

        topic_info = self.topic_model.get_topic_by_topic_id(topic_id)

        if(not topic_info["author_id"] == self.current_user["uid"]):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_permission"] = [u"没有权限修改该话题"]
            self.get(topic_id, template_variables)
            return

        update_topic_info = {
            "title": form.title.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "updated": time.strftime('%Y-%m-%d %H:%M:%S'),
            "last_touched": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.topic_model.update_topic_by_topic_id(topic_id, update_topic_info)

        # create @username notification

        for username in set(find_mentions(form.content.data)):
            mentioned_user = self.user_model.get_user_by_username(username)

            if not mentioned_user:
                continue

            if mentioned_user["uid"] == self.current_user["uid"]:
                continue

            if mentioned_user["uid"] == topic_info["author_id"]:
                continue

            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 2, # 0: mention, 1: comment, 2: topic mention, 3: topic reply
                "involved_user_id": mentioned_user["uid"],
                "involved_post_id": topic_id,
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        self.redirect("/t/%s" % topic_id)


class ReplyEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, reply_id, template_variables = {}):
        user_info = self.current_user
        template_variables["active_page"] = "forum"
        template_variables["user_info"] = user_info
        template_variables["reply"] = self.reply_model.get_reply_by_reply_id(reply_id)
        template_variables["gen_random"] = gen_random
        self.render("topic/reply_edit.html", **template_variables)

    @tornado.web.authenticated
    def post(self, reply_id, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = ReplyEditForm(self)

        if not form.validate():
            self.get(reply_id, {"errors": form.errors})
            return

        # continue while validate succeed

        reply_info = self.reply_model.get_reply_by_reply_id(reply_id)

        if(not reply_info["author_id"] == self.current_user["uid"]):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_permission"] = [u"没有权限修改该回复"]
            self.get(reply_id, template_variables)
            return

        update_reply_info = {
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "updated": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        reply_id = self.reply_model.update_reply_by_reply_id(reply_id, update_reply_info)

        # create @username notification

        for username in set(find_mentions(form.content.data)):
            mentioned_user = self.user_model.get_user_by_username(username)

            if not mentioned_user:
                continue

            if mentioned_user["uid"] == self.current_user["uid"]:
                continue

            if mentioned_user["uid"] == reply_info["author_id"]:
                continue

            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 2, # 0: mention, 1: comment, 2: topic mention, 3: topic reply
                "involved_user_id": mentioned_user["uid"],
                "involved_post_id": reply_info["topic_id"],
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        self.redirect("/t/%s" % reply_info["topic_id"])