#! -*- coding: utf-8 -*-

import time
import tornado.web
from base import BaseHandler
from lib import PageMixin, md_to_html, unicode_truncate


class IdeaListHandler(BaseHandler, PageMixin):
    def get(self):
#        ideas=self.db['Idea'].find().sort('date',-1).limit(9)
        ideas = self.db['Idea'].find().sort('date', -1)
#        count=self.db['Idea'].find().count()
        p = self.db['Idea'].find().count() / 9
#        p = self._get_page()
        page = self._get_pagination(ideas, perpage=9)
        self.render("ideaList.html", ideas=ideas, page=page, p=p)


class NewIdeaHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.render('new_idea.html')
        else:
            self.flash("请先登陆后再进行操作", "error")
            self.redirect('/account/signin')

    def post(self):
        title = self.get_argument("title", None)
        content_md = self.get_argument("content_md", None)
        content_html = md_to_html(content_md)
        if not (title and content_md):
#            self.flash_message('请输入标题和正文！', 'error')
            self.render('new_idea.html')
            return
        iid = self.db.auto_inc.find_and_modify(update={"$inc": {"idea_id": 1}},
                                               query={"name": "idea_id"},
                                               new=True).get("idea_id")
        self.db['Idea'].save({'author': self.get_current_user(),
                              'date': time.time(),
                              'title': title,
                              'content_md': content_md,
                              'content_html': content_html,
                              "reply_count": 0,
                              'progress': '启动中',
                              'iid': iid})
        self.redirect("/idea")


class EditIdeaHandler(BaseHandler):
    def get(self, idea_id):
        idea = self.db['Idea'].find_one({'iid': int(idea_id)})
        url = '/idea/' + idea_id
        if self.get_current_user() == idea['author']:
            self.render('edit_idea.html', idea=idea, url=url)
        else:
            self.redirect(url)

    def post(self, idea_id):
        title = self.get_argument('title', '')
        content_md = self.get_argument('content_md', '')
        progress = self.get_argument('progress', '')
        url = '/idea/' + idea_id
        if not (title and content_md):
            self.flash('表单不允许为空！', 'error')
            return self.redirect(url + '/edit')

        self.db['Idea'].update({'iid': int(idea_id)},
                               {"$set":
                                {"title": title,
                                 "content_md": content_md,
                                 "content_html": md_to_html(content_md),
                                 "progress": progress}})
        self.redirect(url)


class IdeaHanler(BaseHandler):
    def get(self, iid=None):
        idea = self.db['Idea'].find_one({"iid": int(iid)})
        member = self.get_member(idea['author'])
        replies = self.db['reply_Idea'].find({'iid': iid}, sort=[('time', -1)])
        self.render('idea.html', idea=idea, replies=replies, member=member)

    def post(self, iid):
        content = self.get_argument('content', None)
        url = "/idea/" + iid
        if not content:
            self.flash('请不要发送空评论！', 'error')
            self.redirect(url)
            return
        elif len(content) > 250:
            self.flash("回复内容超字数，请惜字如金", "error")
            self.redirect(url)
            return
        self.db['Idea'].update({"iid": int(iid)}, {"$inc": {"reply_count": 1}})
        self.db['reply_Idea'].save({"content": content,
                                    "author": self.get_current_user(),
                                    "time": time.time(),
                                    "iid": iid})
        self.redirect(url)


class IdeaListModule(tornado.web.UIModule):
    def render(self, ideas):
        return self.render_string("module/idea_list.html", ideas=ideas,
                                  unicode_truncate=unicode_truncate)


class IdeaPaginatorModule(tornado.web.UIModule):
    def render(self, page, p):
        return self.render_string('module/idea_paginator.html', page=page, p=p)


class MemberIdeaListModule(tornado.web.UIModule):       
    def render(self,ideas):
        return self.render_string("module/member_idea_list.html", ideas=ideas)
    

handlers = [
    (r'/idea', IdeaListHandler),
    (r'/idea/new_idea', NewIdeaHandler),
    (r'/idea/(\w+)/edit', EditIdeaHandler),
    (r'/idea/(\w+)', IdeaHanler)]

ui_modules = {
    'IdeaListModule':IdeaListModule,
    'IdeaPaginatorModule':IdeaPaginatorModule,
    'MemberIdeaListModule':MemberIdeaListModule}
