# -*- coding: utf-8 -*-

from handlers import account
from handlers import topic
from handlers import node
from handlers import member

from handlers import idea


__all__ = ['handlers', 'ui_modules']

handlers = []
handlers.extend(account.handlers)
handlers.extend(topic.handlers)
handlers.extend(node.handlers)
handlers.extend(member.handlers)
handlers.extend(idea.handlers)


ui_modules = {}
ui_modules.update(**topic.ui_modules)
ui_modules.update(**member.ui_modules)
ui_modules.update(**idea.ui_modules)
