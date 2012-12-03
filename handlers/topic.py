# -*- coding: utf-8 -*-

import time
import tornado.web
from base import BaseHandler
from lib import *

class TopicListHandler(BaseHandler, PageMixin):
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
        replies = self.db.reply.find({"tid": int(topic_id)}, sort=[('last_reply_time', -1)])
        
        self.render("topic.html", topic=topic, replies=replies)

    def post(self, topic_id):
        content_md = self.get_argument('content_md', None)

        if not content_md:
            self.flash('请填写回复内容', "error")
            return
        elif len(content_md) > 20000:
            self.flash("回复内容太长了:(", "error")
            return

        reply_time = time.time()
        content_html = md_to_html(content_md)

        reply = {
                'author': self.get_current_user(),
                'create_time': reply_time,
                'tid': int(topic_id),
                'content_md': content_md,
                'content_html': content_html,
        }

        self.db.reply.save(reply)
        self.db.topic.update({"tid": int(topic_id)}, {"$inc": {"reply_count":1}})
        self.db.topic.update({"tid": int(topic_id)}, {"$set": {"last_reply_time": reply_time}})
        url = "/topic/" + topic_id
        self.redirect(url)

class TopicListModule(tornado.web.UIModule):
    def render(self, topics):
        return self.render_string("module/topic_list.html", topics=topics)

class ReplyListModule(tornado.web.UIModule):
    def render(self, replies):
        return self.render_string("module/reply_list.html", replies=replies)

class PaginatorModule(tornado.web.UIModule):
    def render(self, page, p):
        return self.render_string("module/paginator.html", page=page, p=p)

class SystemStatusModule(tornado.web.UIModule):
    def render(self):
        return self.render_string("module/status.html")
        

handlers = [
    (r'/', TopicListHandler),
    (r'/topic/create', NewTopicHandler),
    (r'/topic/(\d+)', TopicHandler),
    (r'/node/(\w+)/create', CreateTopicHandler),
    ]

ui_modules = {
    'TopicListModule': TopicListModule,
    'ReplyListModule': ReplyListModule,
    'PaginatorModule': PaginatorModule,
    'SystemStatusModule': SystemStatusModule,
    }
