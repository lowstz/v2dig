# -*- coding: utf-8 -*-

import time
from base import BaseHandler
from lib import *


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
            self.redirect(u"/")
            return
        
        self.flash('Invalid username or password', 'error')
        self.render('signin.html')

class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u'/account/signin')
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

class SettingHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            user = self.db.user.find_one({"username": self.get_current_user()})
            self.render('setting.html', user=user)
        else:
            self.flash('登陆后在过来', 'error')
            self.redirect('/account/signin')

    def post(self):
        website = self.get_argument('website', '')
        description = self.get_argument('description', '')

        self.db.user.update({"username": self.get_current_user()},
                            {"$set": {"website": website, "description": description}})
        self.flash("个人设置已更新", 'info')
        self.redirect('/account/setting')

class ChangePasswordHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.render('password.html')
        else:
            self.flash('登陆后再过来', 'error')
            self.redirect('/account/signin')

    def post(self):
        old_password = self.get_argument('old_password', None)
        new_password = self.get_argument('new_password', None)
        repeat_password = self.get_argument('repeat_password', None)

        user = self.db.user.find_one({'username': self.get_current_user()})
        
        if not (old_password and new_password and repeat_password):
            self.flash('你至少得输入点东西吧，混蛋', 'error')
            self.redirect('/account/password')

        if new_password != repeat_password:
            self.flash('新密码和重复密码不一样,仔细再修改一次吧！', 'error')
            self.redirect('/account/password')
            
        if not validate_password(str(user['password']), old_password):
            self.flash('输入的旧密码不正确，请在多次几次', 'error') 
            self.redirect('/account/password')
        
        self.db.user.update({"username": self.get_current_user()},
                            {"$set": {"password": encrypt_password(new_password)}})
        self.flash('密码修改完成, 请重新登陆', 'info')
        self.redirect('/account/signout')

handlers = [
    (r'/account/signup', RegisterHandler),
    (r'/account/signin', SigninHandler),
    (r'/account/signout', SignoutHandler),
    (r'/account/setting', SettingHandler),
    (r'/account/password', ChangePasswordHandler),
    ]

ui_modules = {}
