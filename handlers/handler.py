#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
import time

from tornado.httpclient import *
from tornado.web import url
import tornado.web
import tornado.escape
import time

from lib import *
from cache import cache
from lib import *
username_validator = re.compile(r'^[a-zA-Z0-9]+$')
email_validator = re.compile(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE)


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

    # def get_current_user(self):
    #     is_auth = self.get_secure_cookie("is_auth")
    #     interval = 10

    #     if not is_auth:
    #         # This is a guest or offline user
    #         # guest cookie has below:
    #         # guest_id:
    #         # locale:
    #         # count:

    #         guest_id = self.get_secure_cookie("guest_id")
    #         count = self.get_secure_cookie("count")

    #         if guest_id and count:
    #             count = int(count)
    #             if count / interval == 1:
    #                 count = 0
    #         else:
    #             if guest_id:
    #                 self.set_secure_cookie("guest_id", guest_id)
    #                 count = 0
    #             else:
    #                 raise HTTPError(500)
    #         self.set_secure_cookie("count", str(count + 1))
            

    #         # This is a online user

    #         user = {
    #             "user_id": self.get_secure_cookie("user_id"),
    #             "username": self.get_secure_cookie("username")
    #             }
    #         is_auth = int(is_auth)
    #         if is_auth / interval == 1:
    #             is_auth = 0
    #         user["is_auth"] = True
    #         self.set_secure_cookie("is_auth", str(is_auth + 1))
    #         return user

    # source from  https://github.com/lepture/july/blob/master/july/web.py
    def flash_message(self, msg=None, category=None):
        """flash_message provide an easy way to communicate with users.

        create message in your handler::

            class HomeHandler(JulyHandler):
                def get(self):
                    self.flash_message('thanks')
                    self.render('home.html')

        and get messages in ``home.html``::

            <ul>
                {% for category, message in flash_message() $}
                <li>{{category}}: {{message}}</li>
                {% end %}
            </ul>
        """
        def get_category_message(messages, category):
            for cat, msg in messages:
                if cat == category:
                    yield (cat, msg)

        #: use xsrf token or not ?
        key = '%s_flash_message' % self.xsrf_token
        if msg is None:
            messages = cache.get(key)
            if messages is None:
                return []
            if category is not None:
                return get_category_message(messages, category)

            #: clear flash message
            cache.delete(key)
            return messages
        message = (category, msg)
        messages = cache.get(key)
        if isinstance(messages, list):
            messages.append(message)
        else:
            messages = [message]
        cache.set(key, messages, 600)
        return message

        
        
class IndexHandler(BaseHandler):
    def get(self):
        self.render('home.html')

class LoginHandler(BaseHandler):
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
            self.redirect(u"/")
            return
        
        self.flash_message('Invalid username or password', 'error')
        self.render('signin.html')
        
class RegisterHandler(BaseHandler):
    def get(self):
        self.render("signup.html")
        
    def post(self):
        username = self.get_argument("username", None)
        email = self.get_argument("email", "").lower()
        password = self.get_argument("password", None)
        repeat_password = self.get_argument("repeat_password", None)
        if not (username and email and password and repeat_password):
            self.flash_message('Please fill the require fields', 'error')
            self.render('signup.html')

        if password != repeat_password:
            self.flash_message("Password doesn't match", 'error')
        elif username and not username_validator.match(username):
            self.flash_message('Username is invalid', 'error')
        elif email and not email_validator.match(email):
            self.flash_message('Not a valid email address', 'error')
        elif username and self.db.user.find_one({'username': username}):
            self.flash_message('This username is already registered', 'error')

        if email and self.db.user.find_one({'email' : email}):
            self.flash_message('This email is already registered', 'warn')
        elif email and self.db.user.find_one({'email' : email}):
            self.flash_message('This email is already registered', 'error')
        else:
            hashed_password = encrypt_password(password)
            uid = self.db.auto_inc.find_and_modify(
                update={"$inc": {"user_id":1}},
                new=True
                ).get("user_id")
            
            user = {
                "username": username,
                "password": hashed_password,
                "email": email,
                "registered_time": time.time(),
                "uid": uid,
                "description": "",
                "website": "",
                "last_accesse_time": time.time(),
                }

            if self.db.user.save(user):
                self.redirect(u"/account/signin")
                #                self.flash_message("A active email has already been send to " + email + ", Please active your account before login.")

                
                
class IdeaHandler(BaseHandler):
    def get(self):
        import idea_lib
        ceshi=self.db['user'].find_one({'username':'lowstz'})
        self.render("idea.html",sb_text=idea_lib.Test(ceshi,'email'))
#        self.render("idea.html",sb_text=ceshi['email'])
        self.flash_message('Please fill the required fields', 'error')
    def post(self):
        tex1=self.get_argument("tef")
        tex2=self.get_argument("tes")
        self.render("topic.html",page_title=tex1,header_text=tex2)
#        tl= self.db['user'].insert({ 'name': tex1,'blog':
#                                    {"Time":time.time(),"e":tex2,}  })插入的尝试

#        t=self.db['user'].update({'user':'sw78'},{"$push":{"comments":{"time":tex1,"xx":tex2}}})
#插入评论

# Toolkit
class NewIdeaHandler(BaseHandler):
    def get(self):
        self.render('new_idea.html')
    def post(self):
        title=self.get_argument("title",None)
        content=self.get_argument("content",None)
        if not (title and content):
#            self.flash_message('请输入标题和正文！', 'error')
            self.render('new_idea.html')
            return
        self.db['Idea'].insert({'username':'csw','date':time.time(),'tag':'sbq','title':title,\
                                'text':content, "click" : 0, "id" : 1, "comment" : ""})
        self.redirect("/idea")

class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u'/')


class HomeHandler(BaseHandler):
    pass


def send_verify_email(request_handler, email_address, username, password):
    subject = tornado.escape.to_unicode("Active account email from v2dig") 
    message = tornado.escape.url_escape(tornado.escape.to_unicode(request_handler.render_string("active_email.html", username=username, password=password)))
    body='_xsrf='+ request_handler.xsrf_token + "&receiver="+ email_address +'&subject=' + subject + '&plain=' + message + "&html=" + message
    http_client = AsyncHTTPClient()
    request = request_handler.request
    http_client.fetch(request.protocol + "://" + request.host + "/sendmail", None, method="POST", body=body, headers = request.headers)
        

# Handler
handlers = [
    url(r'/', IndexHandler),
    url(r'/account/signup', RegisterHandler),
    url(r'/account/signin', LoginHandler),
    url(r'/idea',IdeaHandler),
    url(r'/idea/new_idea',NewIdeaHandler),
    url(r'/account/signout', SignoutHandler),
]

#TODO - HomeHandler
#TODO - 注册部分验证码
#TODO - TopicHandler

