#! -*- coding: utf-8 -*-

from base import BaseHandler 
from lib import PageMixin

class NodeListHandler(BaseHandler, PageMixin):
    def get(self, node_name):
        topics = self.db.topic.find({'node': node_name}, sort=[('last_reply_time', -1)])
        node = self.get_node(node_name)
        p = self._get_page()
        page = self._get_pagination(topics, perpage=20)
        self.render('node.html', topics=topics, node=node, page=page, p=p)

class CreateNodeHandler(BaseHandler):
    def get(self):
        pass
    
handlers = [
    (r'/node/(\w+)', NodeListHandler),
    ]
