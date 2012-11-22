#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pymongo
import tornado.httpserver
import tornado.ioloop
import tornado.web

from tornado.options import define, options

ROOT = os.path.abspath(os.path.dirname(__file__))
define("port", default=8000, help="run on the given port", type=int)
define('settings', default=os.path.join(ROOT, 'settings.py'),
       help='path to the settings file.', type=str)

from database import *
import ui_methods

class Application(tornado.web.Application):
    def __init__(self):
        from urls import handlers, ui_modules
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="g1VaSuEUQPeZ3o7tNw+kQN1FVP49qUezrDhWQjaLREA=",
            ui_modules=ui_modules,
            ui_methods=ui_methods,
            debug=True,
            )
        execfile(options.settings, {}, settings)
        super(Application,self).__init__(handlers, **settings)
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = db

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
