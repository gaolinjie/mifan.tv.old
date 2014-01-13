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
import urllib
import tornado.web
import lib.jsonp
import os.path

from base import *
from form.topic import *
from lib.sendmail import send
from lib.variables import gen_random
from lib.gravatar import Gravatar
from form.user import *

from lib.utils import find_video_id_from_url

class ChannelSettingHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            plus = self.plus_model.get_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                template_variables["followed"]=1;
            else:
                template_variables["followed"]=0;
            if(plus):
                template_variables["plused"]=1;
            else:
                template_variables["plused"]=0;
            template_variables["channel"] = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
        else:
            self.redirect("/login")

        self.render("channel/channel_setting.html", **template_variables)

    @tornado.web.authenticated
    def post(self, channel_id, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = SettingForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed

        user_info = self.current_user
        update_result = self.channel_model.update_channel_info_by_channel_id(channel_id, {
            "intro": form.self_intro.data,
        })

        self.redirect("/c/" + channel_id)

class ChannelSettingAvatarHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, channel_id, template_variables = {}):
        user_info = self.get_current_user()
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            plus = self.plus_model.get_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                template_variables["followed"]=1;
            else:
                template_variables["followed"]=0;
            if(plus):
                template_variables["plused"]=1;
            else:
                template_variables["plused"]=0;
            template_variables["channel"] = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
        else:
            self.redirect("/login")

        self.render("channel/channel_setting_avatar.html", **template_variables)

    @tornado.web.authenticated
    def post(self, channel_id, template_variables = {}):
        template_variables = {}
        print channel_id

        if(not "avatar" in self.request.files):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_avatar"] = [u"请先选择要上传的头像"]
            self.get(template_variables)
            return

        user_info = self.current_user

        avatar_name = "%s" % uuid.uuid5(uuid.NAMESPACE_DNS, str(channel_id))
        avatar_raw = self.request.files["avatar"][0]["body"]
        avatar_buffer = StringIO.StringIO(avatar_raw)
        avatar = Image.open(avatar_buffer)

        # crop avatar if it's not square
        avatar_w, avatar_h = avatar.size
        avatar_border = avatar_w if avatar_w < avatar_h else avatar_h
        avatar_crop_region = (0, 0, avatar_border, avatar_border)
        avatar = avatar.crop(avatar_crop_region)

        avatar_128x128 = avatar.resize((128, 128), Image.ANTIALIAS)
        avatar_96x96 = avatar.resize((96, 96), Image.ANTIALIAS)
        avatar_48x48 = avatar.resize((48, 48), Image.ANTIALIAS)
        
        usr_home = os.path.expanduser('~')
        avatar_128x128.save(usr_home+"/www/mifan.tv/static/avatar/channel/b_%s.png" % avatar_name, "PNG")
        avatar_96x96.save(usr_home+"/www/mifan.tv/static/avatar/channel/m_%s.png" % avatar_name, "PNG")
        avatar_48x48.save(usr_home+"/www/mifan.tv/static/avatar/channel/s_%s.png" % avatar_name, "PNG")
        
        result = self.channel_model.set_channel_avatar_by_channel_id(channel_id, "%s.png" % avatar_name)
        template_variables["success_message"] = [u"频道头像更新成功"]

        self.redirect("/c/"+channel_id)

class ChannelSettingCoverHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, channel_id, template_variables = {}):
        user_info = self.get_current_user()
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            plus = self.plus_model.get_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                template_variables["followed"]=1;
            else:
                template_variables["followed"]=0;
            if(plus):
                template_variables["plused"]=1;
            else:
                template_variables["plused"]=0;
            template_variables["channel"] = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
        else:
            self.redirect("/login")

        self.render("channel/channel_setting_cover.html", **template_variables)

    @tornado.web.authenticated
    def post(self, channel_id, template_variables = {}):
        template_variables = {}
        print channel_id

        if(not "avatar" in self.request.files):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_cover"] = [u"请先选择要上传的封面"]
            self.get(template_variables)
            return

        user_info = self.current_user

        cover_name = "%s" % uuid.uuid5(uuid.NAMESPACE_DNS, str(channel_id))
        cover_raw = self.request.files["avatar"][0]["body"]
        cover_buffer = StringIO.StringIO(cover_raw)
        cover = Image.open(cover_buffer)

        cover_520x260 = cover.resize((520, 260), Image.ANTIALIAS)
     
        usr_home = os.path.expanduser('~')
        cover_520x260.save(usr_home+"/www/mifan.tv/static/cover/channel/m_%s.png" % cover_name, "PNG")
        
        result = self.channel_model.set_channel_cover_by_channel_id(channel_id, "%s.png" % cover_name)
        template_variables["success_message"] = [u"频道头像更新成功"]

        self.redirect("/c/"+channel_id)


class VideoHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "video"
        template_variables["active_tab"] = tab
        if(user_info):
            notice_text = "暂时还没有短片频道"
            template_variables["notice_text"] = notice_text
            template_variables["active_tab"] = tab
            template_variables["subnavs"] = self.subnav_model.get_subnavs_by_nav_id(1)
            if (tab=="all"):
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id(1, user_info["uid"], current_page = page)
            else:
                subnav_id = self.subnav_model.get_subnav_by_subnav_name(tab).id
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id_and_subnav_id(1, user_info["uid"], subnav_id, current_page = page)
        else:
            self.redirect("/login")

        self.render("video.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = ChannelForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed


        subnav_id = self.subnav_model.get_subnav_by_subnav_title(form.subnav.data).id
        channel_info = {
            "name": form.name.data,
            "intro": form.intro.data,
            "nav_id": 1,
            "subnav_id": subnav_id,
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
        self.redirect("/video")

class FollowsHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "followed")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            template_variables["active_nav"] = "follow"
            template_variables["active_tab"] = tab
            notice_text = "你还未关注任何频道"

            if (tab=="followed"):
                notice_text = "你还未关注任何频道"
                template_variables["channels"] = self.follow_model.get_user_all_only_follow_channels(user_info["uid"], current_page = page)
            elif (tab=="created"):
                notice_text = "你还未创建任何频道"
                template_variables["channels"] = self.channel_model.get_user_all_channels(user_info["uid"], current_page = page)

            template_variables["notice_text"] = notice_text
        else:
            self.redirect("/login")

        self.render("follow.html", **template_variables)

class SuggestionsHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            template_variables["channels"] = self.channel_model.get_hot_channels(user_info["uid"], current_page = page)
            notice_text = "对不起，暂时没有频道推荐给你"
            template_variables["notice_text"] = notice_text
        else:
            self.redirect("/login")

        self.render("channel/suggestions.html", **template_variables)

class HotChannelsHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            notice_text = "还没有热门频道"
            template_variables["notice_text"] = notice_text
            template_variables["active_tab"] = tab
            if(tab=="all"):
                template_variables["channels"] = self.channel_model.get_hot_channels(user_info["uid"], current_page = page)
            else:
                nav_id=1
                if (tab=="video"):
                    nav_id=1
                if (tab=="micro"):
                    nav_id=2
                if (tab=="movie"):
                    nav_id=3
                if (tab=="star"):
                    nav_id=4
                template_variables["channels"] = self.channel_model.get_hot_channels_by_nav_id(user_info["uid"], nav_id, current_page = page)            
        else:
            self.redirect("/login")

        self.render("channel/hot_channels.html", **template_variables)

class UserOtherChannelsHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            if(re.match(r'^\d+$', user)):
                view_user_info = self.user_model.get_user_by_uid(user)
            else:
                view_user_info = self.user_model.get_user_by_username(user)
            template_variables["view_user_info"] = view_user_info
            template_variables["active_tab"] = tab
            if(tab=="all"):
                template_variables["channels"] = self.channel_model.get_user_all_channels(view_user_info["uid"], current_page = page)
                notice_text = "TA还没创建频道"
            else:
                nav_id=1
                if (tab=="video"):
                    nav_id=1
                    notice_text = "TA还没创建短片频道"
                if (tab=="micro"):
                    nav_id=2
                    notice_text = "TA还没创建微电影频道"
                if (tab=="movie"):
                    nav_id=3
                    notice_text = "TA还没创建电影频道"
                if (tab=="star"):
                    nav_id=4
                    notice_text = "TA还没创建明星频道"
                template_variables["channels"] = self.channel_model.get_user_all_channels_by_nav_id(view_user_info["uid"], nav_id, current_page = page)
            
            template_variables["notice_text"] = notice_text
        else:
            self.redirect("/login")

        self.render("channel/user_other_channels.html", **template_variables)

class SearchChannelHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            page = int(self.get_argument("page", "1"))
        else:
            self.redirect("/login")

        self.render("channel/search_channel.html", **template_variables)

class MicroHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "micro" 

        tab = self.get_argument('tab', "all")
        template_variables["active_tab"] = tab
        notice_text = "暂时还没有微电影频道"
        template_variables["notice_text"] = notice_text
        template_variables["subnavs"] = self.subnav_model.get_subnavs_by_nav_id(2)
        if(user_info):         
            if (tab=="all"):
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id(2, user_info["uid"], current_page = page)
            else:
                subnav_id = self.subnav_model.get_subnav_by_subnav_name(tab).id
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id_and_subnav_id(2, user_info["uid"], subnav_id, current_page = page)
        else:
            self.redirect("/login")

        self.render("micro.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = ChannelForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed


        subnav_id = self.subnav_model.get_subnav_by_subnav_title(form.subnav.data).id
        channel_info = {
            "name": form.name.data,
            "intro": form.intro.data,
            "nav_id": 2,
            "subnav_id": subnav_id,
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
        self.redirect("/micro")


class MovieHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "movie" 

        tab = self.get_argument('tab', "all")
        template_variables["active_tab"] = tab
        notice_text = "暂时还没有电影频道"
        template_variables["notice_text"] = notice_text
        template_variables["subnavs"] = self.subnav_model.get_subnavs_by_nav_id(3)
        if(user_info):         
            if (tab=="all"):
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id(3, user_info["uid"], current_page = page)
            else:
                subnav_id = self.subnav_model.get_subnav_by_subnav_name(tab).id
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id_and_subnav_id(3, user_info["uid"], subnav_id, current_page = page)
        else:
            self.redirect("/login")

        self.render("movie.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = ChannelForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed


        subnav_id = self.subnav_model.get_subnav_by_subnav_title(form.subnav.data).id
        channel_info = {
            "name": form.name.data,
            "intro": form.intro.data,
            "nav_id": 3,
            "subnav_id": subnav_id,
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
        self.redirect("/movie")

class TVHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "tv" 

        tab = self.get_argument('tab', "all")
        template_variables["active_tab"] = tab
        notice_text = "暂时还没有明星频道"
        template_variables["notice_text"] = notice_text
        template_variables["subnavs"] = self.subnav_model.get_subnavs_by_nav_id(4)
        if(user_info):         
            if (tab=="all"):
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id(4, user_info["uid"], current_page = page)
            else:
                subnav_id = self.subnav_model.get_subnav_by_subnav_name(tab).id
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id_and_subnav_id(4, user_info["uid"], subnav_id, current_page = page)
        else:
            self.redirect("/login")

        self.render("star.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = ChannelForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed


        subnav_id = self.subnav_model.get_subnav_by_subnav_title(form.subnav.data).id
        channel_info = {
            "name": form.name.data,
            "intro": form.intro.data,
            "nav_id": 4,
            "subnav_id": subnav_id,
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
        self.redirect("/tv")

class StarHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "star" 

        tab = self.get_argument('tab', "all")
        template_variables["active_tab"] = tab
        notice_text = "暂时还没有明星频道"
        template_variables["notice_text"] = notice_text
        template_variables["subnavs"] = self.subnav_model.get_subnavs_by_nav_id(4)
        if(user_info):         
            if (tab=="all"):
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id(4, user_info["uid"], current_page = page)
            else:
                subnav_id = self.subnav_model.get_subnav_by_subnav_name(tab).id
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id_and_subnav_id(4, user_info["uid"], subnav_id, current_page = page)
        else:
            self.redirect("/login")

        self.render("star.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = ChannelForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed


        subnav_id = self.subnav_model.get_subnav_by_subnav_title(form.subnav.data).id
        channel_info = {
            "name": form.name.data,
            "intro": form.intro.data,
            "nav_id": 4,
            "subnav_id": subnav_id,
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
        self.redirect("/star")

class ChannelHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            channel = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
            author_info = self.user_model.get_user_by_uid(channel.author_id)
            template_variables["author_info"] = author_info
            template_variables["user_other_channels"] = self.channel_model.get_user_other_channels(author_info["uid"], channel_id)
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                template_variables["followed"]=1;
            else:
                template_variables["followed"]=0;

            template_variables["channel"] = channel
            template_variables["posts"] = self.post_model.get_all_posts_by_channel_id(current_page = page, user_id = user_info["uid"], channel_id = channel_id)
        else:
            self.redirect("/login")

        self.render("channel/channel.html", **template_variables)

    @tornado.web.authenticated
    def post(self, channel_id, template_variables = {}):
        template_variables = {}
        user_info = self.current_user

        # validate the fields
        form = PostForm2(self)

        if not form.validate():
            self.get(channel_id, {"errors": form.errors})
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

        channel = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
        
        post_info = {
            "author_id": self.current_user["uid"],
            "channel_id": channel_id,
            "nav_id": channel["nav_id"],
            "video_id": vid,
            "intro": form.intro.data,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.post_model.add_new_post(post_info)
        self.channel_model.update_channel_info_by_channel_id(channel.id, {"plus":channel.plus+3, "posts": channel.posts+1})
        self.user_model.update_user_info_by_user_id(user_info["uid"], {"plus":user_info["plus"]+3})

        self.redirect("/c/" + channel_id)

class FollowHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            channel = self.channel_model.get_channel_by_channel_id(channel_id)
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                self.follow_model.delete_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_followed",
                }))
                self.channel_model.update_channel_info_by_channel_id(channel_id, {"followers": channel.followers-1})
            else:
                channel = self.channel_model.get_channel_by_channel_id(channel_id)
                follow_info = {
                    "user_id": user_info["uid"],
                    "channel_id": channel_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.follow_model.add_new_follow(follow_info)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_followed",
                }))
                self.channel_model.update_channel_info_by_channel_id(channel_id, {"followers": channel.followers+1})
