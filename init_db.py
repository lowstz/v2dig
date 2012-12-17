#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database import *

idea_id = {
    'idea_id': int(0),
    'name': 'idea_id'}
    
topic_id = {
    'topic_id': int(0),
    'name': 'topic_id'}

user_id = {
    'user_id': int(0),
    'name': 'user_id'}

db.auto_inc.save(idea_id)
db.auto_inc.save(topic_id)
db.auto_inc.save(user_id)

