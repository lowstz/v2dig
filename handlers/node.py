#! -*- coding: utf-8 -*-

from base import BaseHandler 
from lib import PageMixin

class NodeListHandler(BaseHandler, PageMixin):
    def get(self, node_name):
        topics = self.db.topic.find({'node': node_name}, 
                                    sort=[('last_reply_time', -1)])
        node = self.get_node(node_name)
        p = self._get_page()
        page = self._get_pagination(topics, perpage=20)
        self.render('node.html', topics=topics, node=node, page=page, p=p)

class CreateNodeHandler(BaseHandler):
    def get(self):
        if self.is_admin():
            self.render('create_node.html')
        else:
            self.set_status(403)

    def post(self):
        node_name = self.get_argument('node_name', None)
        node_title = self.get_argument('node_title', None)
        description = self.get_argument('description', None)

        if not (node_name and node_title and description):
            self.flash('请填点东西吧', 'error')
            self.redirect('/dashboard/create_node')
        new_node = {}
        new_node['node_name'] = node_name.lower()
        new_node['node_title'] = node_title
        new_node['description'] = description
        
        self.db.node.save(new_node)
        self.redirect('/dashboard/create_node')
    
handlers = [
    (r'/node/(\w+)', NodeListHandler),
    (r'/dashboard/create_node', CreateNodeHandler),
    ]


## TODO: 节点创建
