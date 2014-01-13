#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

from wtforms import TextField, HiddenField, validators
from lib.forms import Form

class ReplyForm(Form):
    content = TextField('Content', [
        validators.Required(message = "请填写回复内容"),
    ])

    tid = TextField('Tid', [
        validators.Required(message = "要回复的帖子不明确"),
    ])

class PostForm(Form):
    intro = TextField('Intro', [
        validators.Required(message = "请填写视频介绍"),
        validators.Length(min = 6, message = "介绍长度过短（3-140个字符）"),
        validators.Length(max = 280, message = "介绍长度过长（3-140个字符）"),
    ])

    link = TextField('Link', [
        validators.Required(message = "请填写视频链接"),
    ])

    channel = TextField('Channel', [
        validators.Required(message = "请选择视频频道"),
    ])

class PostForm2(Form):
    intro = TextField('Intro', [
        validators.Required(message = "请填写视频介绍"),
        validators.Length(min = 3, message = "介绍长度过短（3-56个字符）"),
        validators.Length(max = 156, message = "介绍长度过长（3-56个字符）"),
    ])

    link = TextField('Link', [
        validators.Required(message = "请填写视频链接"),
    ])

class ChannelForm(Form):
    intro = TextField('Intro', [
        validators.Required(message = "请填写频道介绍"),
        validators.Length(min = 3, message = "介绍长度过短（3-56个字符）"),
        validators.Length(max = 156, message = "介绍长度过长（3-56个字符）"),
    ])

    name = TextField('Name', [
        validators.Required(message = "请填写频道名称"),
    ])

    subnav = TextField('Subnav', [
        validators.Required(message = "请选择频道类别"),
    ])

class ChannelForm2(Form):
    intro = TextField('Intro', [
        validators.Required(message = "请填写频道介绍"),
        validators.Length(min = 3, message = "介绍长度过短（3-56个字符）"),
        validators.Length(max = 156, message = "介绍长度过长（3-56个字符）"),
    ])

    name = TextField('Name', [
        validators.Required(message = "请填写频道名称"),
    ])

    nav = TextField('Nav', [
        validators.Required(message = "请选择频道类别"),
    ])


class ReplyEditForm(Form):
    content = TextField('Content', [
        validators.Required(message = "请填写回复内容"),
    ])

class CreateMessageForm(Form):
    content = TextField('Content', [
        validators.Required(message = "请填写帖子内容"),
    ])

class CreateForm(Form):
     title = TextField('Title', [
         validators.Required(message = "请填写帖子标题"),
         validators.Length(min = 3, message = "帖子标题长度过短（3-56个字符）"),
         validators.Length(max = 56, message = "帖子标题长度过长（3-56个字符）"),
     ])
 
     content = TextField('Content', [
         validators.Required(message = "请填写帖子内容"),
     ])