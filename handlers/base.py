# -*- coding: utf-8 -*-

import time
import hashlib
import sys
import settings
import tornado.web
import tornado.escape
sys.path.append('..')

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    def get_current_user(self):
        user = self.get_secure_cookie('user')
        if user:
            return user
        else: 
            return None

    def flash(self, message, category='message'):
        messages = self.messages()
        messages.append((category, message))
        self.set_secure_cookie('flash_messages',
                               tornado.escape.json_encode(messages))
    
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
            return None
        return member

    def get_node(self, node_name):
        node = self.db.node.find_one({'node_name': node_name})
        if not node:
            raise tornado.web.HTTPError(404)
        return node
        
    def get_avatar(self, email, size=48):
        md5email = hashlib.md5(email).hexdigest()
        query = "%s?s=%s" % (md5email, size)
        return settings.gravatar_base_url + query

    def format_time(self, unixtime):
        t = time.localtime(unixtime)
        formated_time = time.strftime('%Y-%m-%d %H:%M:%S', t)
        return formated_time

    def is_admin(self):
        user =  self.get_member(self.get_current_user())
        if user:
            if user['role'] == 3:
                return True
            else:
                return False
