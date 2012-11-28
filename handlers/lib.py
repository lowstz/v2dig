#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import hashlib
import markdown

username_validator = re.compile(r'^[a-zA-Z0-9]+$')
email_validator = re.compile(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE)


def encrypt_password(password):
    """Hash password on the fly."""
    m = hashlib.md5()
    m.update(password)
    password = m.hexdigest().upper()
    return password


def validate_password(hashed, input_password):
    return hashed == encrypt_password(input_password)

def md_to_html(content_md):
    content_html = markdown.markdown(content_md, ['codehilite', 'fenced_code'])
    return content_html


class PageMixin(object):
    def _get_order(self):
        if not hasattr(self, 'get_argument'):
            self.get_argument = self.handler.get_argument
        order = self.get_argument('o', '0')
        if order == '1':
            return '-id'
        return '-impact'

    def _get_page(self):
        if not hasattr(self, 'get_argument'):
            self.get_argument = self.handler.get_argument
        page = self.get_argument('p', '1')
        try:
            return int(page)
        except:
            return 1

    def _get_pagination(self, q, count=None, perpage=20):
        page = self._get_page()
        start = (page - 1) * perpage
        end = page * perpage
        if not count:
            count = q.count()

        dct = {}
        page_number = (count - 1) / perpage + 1  # this algorithm is fabulous
        dct['page_number'] = page_number
        dct['datalist'] = q[start:end]
        if page < 5:
            dct['pagelist'] = range(1, min(page_number, 9) + 1)
        elif page + 4 > page_number:
            dct['pagelist'] = range(max(page_number - 8, 1), page_number + 1)
        else:
            dct['pagelist'] = range(page - 4, min(page_number, page + 4) + 1)
        dct['current_page'] = page
        dct['item_number'] = count
        return dct

