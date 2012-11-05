#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
from hashlib import sha256
from hmac import HMAC

from tornado.web import url
import tornado.web
import tornado.escape

from cache import cache

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
        self.render('topic.html')

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
        
class RegisterHandler(LoginHandler):
    def get(self):
        self.render("signup.html", next=self.get_argument("next","/"))
        
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
        if username and not username_validator.match(username):
            self.flash_message('Username is invalid', 'error')
        if email and not email_validator.match(email):
            self.flash_message('Not a valid email address', 'error')
        if username and self.db.user.find_one({'username': username}):
            self.flash_message('This username is already registered', 'error')
        if email and self.db.user.find_one({'email' : email}):
            self.flash_message('This email is already registered', 'warn')
                
                
                

        

# Toolkit
def encrypt_password(password, salt=None):
    """Hash password on the fly."""
    if salt is None:
        salt = os.urandom(8) # 64 bits.

    assert 8 == len(salt)
    assert isinstance(salt, str)

    if isinstance(password, unicode):
        password = password.encode('UTF-8')
        
    assert isinstance(password, str)

    result = password
    for i in xrange(10):
        result = HMAC(result, salt, sha256).digest()

    return salt + result

def validate_password(hashed, input_password):
    return hashed == encrypt_password(input_password, salt=hashed[:8])


# Handler
handlers = [
    url(r'/', IndexHandler),
    url(r'/account/signin', LoginHandler),
    ]

        
    

        
