#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import datetime
import hashlib
import tornado.web
import tornado.escape

from lib import *


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_login_url(self):
        return u"/login"
    
    def get_current_user(self):
        user = self.get_secure_cookie('user')
        if user:
            return user
        else: 
            return None

    def flash(self, message, category='message'):
        messages = self.messages()
        messages.append((category, message))
        self.set_secure_cookie('flash_messages', tornado.escape.json_encode(messages))
    
    def messages(self):
        messages = self.get_secure_cookie('flash_messages')
        messages = tornado.escape.json_decode(messages) if messages else []
        return messages
        
    def get_flashed_messages(self):
        messages = self.messages()
        self.clear_cookie('flash_messages')
        return messages

    def get_member(self, username):
        member = self.db.user.find_one({'username': username})
        if not member:
            raise tornado.web.HTTPError(404)
        return member

    def get_node(self, node_name):
        node = self.db.node.find_one({'node_name': node_name})
        if not node:
            raise tornado.web.HTTPError(404)
        return node
        
    def get_avatar(self, email, size=48):
        md5email = hashlib.md5(email).hexdigest()
        query = "%s?s=%s" % (md5email, size)
        return 'http://cn.gravatar.com/avatar/' + query

    def format_time(self, unixtime):
        t = time.localtime(unixtime)
        formated_time = time.strftime('%Y-%m-%d %H:%M:%S', t)
        return formated_time


class SigninHandler(BaseHandler):
    def get(self):
        self.render('signin.html')

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)

        if not (username and password):
            self.flash_message('Please fill the required fields', 'error')
            self.render('signin.html')
        else:
            user = self.db['user'].find_one({ 'username': username })
            
        if user and validate_password(str(user['password']), password):
            self.set_secure_cookie('user', username)
            self.flash("登陆成功了，亲！", "info")
            self.redirect(u"/")
            return
        
        self.flash('Invalid username or password', 'error')
        self.render('signin.html')

class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.flash("骚年，已经登出帐号", "info")
        self.redirect(u'/')
        return
        
class RegisterHandler(BaseHandler):
    def get(self):
        if self.current_user:
            return self.redirect(u'/')
        self.render("signup.html")
        
    def post(self):
        username = self.get_argument("username", None)
        email = self.get_argument("email", "").lower()
        password = self.get_argument("password", None)
        repeat_password = self.get_argument("repeat_password", None)
        if not (username and email and password and repeat_password):
            self.flash('Please fill the require fields', 'error')
            self.redirect(u"/account/signup")
            return
        
        if password != repeat_password:
            self.flash("Password doesn't match", 'error')
            self.redirect(u"/account/signup")
            return
        
        if username and not username_validator.match(username):
            self.flash('Username is invalid', 'error')
            self.redirect(u"/account/signup")
            return
        
        if email and not email_validator.match(email):
            self.flash('Not a valid email address', 'error')
            self.redirect(u"/account/signup")
        
        if username and self.db.user.find_one({'username': username}):
            self.flash('This username is already registered', 'error')
            self.redirect(u"/account/signup")
            return
        
        if email and self.db.user.find_one({'email' : email}):
            self.flash('This email is already registered', 'error')
            self.redirect(u"/account/signup")
            return
        
        hashed_password = encrypt_password(password)
        uid = self.db.auto_inc.find_and_modify(
            update={"$inc":{"user_id":1}},
            query={"name":"user_id"},
            new=True
            ).get("user_id")
            
        user = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "registered_time": time.time(),
            "uid": uid,
            'role': 1,
            "description": "",
            "website": "",
            "last_accesse_time": time.time(),
            }

        if self.db.user.save(user):
            self.flash("注册成功，可以登入了", "info")
            self.redirect(u"/account/signin")
            ### self.flash_message("A active email has already been send to " + email + ", Please active your account before login.")


class TopicListHandler(BaseHandler, PageMixin):
    def head(self):
        pass
    def get(self):
        topics = self.db.topic.find(sort=[('last_reply_time', -1)])
        p = self._get_page()
        page = self._get_pagination(topics, perpage=12)
        
        self.render("home.html", topics=topics,
                    page=page, p=p)
        

class NewTopicHandler(BaseHandler):
    def get(self):
        nodes = self.db.node.find()
        self.render('new_topic.html', nodes = nodes)
        
        
class CreateTopicHandler(BaseHandler):
    def get(self, node_name):
        if self.get_current_user():
            node = self.db.node.find_one({"node_name":node_name})
            if not node:
                self.send_error(404)
                return
            self.render('create_topic.html', topic=None, node=node)
        else:
            self.flash("骚年，请先登陆后再去刚才那个地方", "error")
            self.redirect('/account/signin')

    def post(self, node_name):
        title = self.get_argument('title', None)
        content_md = self.get_argument('content_md', None)

        if not (title and content_md):
            self.flash("Please fill the required field", "error")
            self.render('create_topic.html', topic=None, node=node)
            return

        tid = self.db.auto_inc.find_and_modify(
            update={"$inc": {"topic_id":1}},
            query={"name":"topic_id"},
            new=True
            ).get("topic_id")

        url = '/topic/' + str(tid)

        topic = dict()
        topic['author'] = self.get_current_user()
        topic['title'] = title
        topic['content_md'] = content_md
        topic['create_time'] = time.time()
        topic['last_reply_time'] = time.time()
        topic['node'] = node_name
        topic['reply_count'] = 0
        topic['tid'] = tid
        topic['content_html'] = md_to_html(content_md)

        self.db.topic.save(topic)
        self.redirect(url)
        

class TopicHandler(BaseHandler):
    def get(self, topic_id):
        topic = self.db.topic.find_one({"tid": int(topic_id)})
        self.render("topic.html", topic=topic)

class ReplyHandler(BaseHandler):
    def get(self, topic_id):
        pass
        
# Handler
handlers = [
    (r'/', TopicListHandler),
    (r'/account/signup', RegisterHandler),
    (r'/account/signin', SigninHandler),
    (r'/account/signout', SignoutHandler),
    (r'/topic/create', NewTopicHandler),
    (r'/topic/(\d+)', TopicHandler),
    (r'/node/(\w+)/create', CreateTopicHandler),
    ]

#TODO - HomeHandler
#TODO - 注册部分验证码
#TODO - TopicHandler

