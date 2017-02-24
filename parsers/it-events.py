# -*- coding: utf-8 -*-
"""
ISAP

Created by pavel on 24.02.17 18:13
"""
from parsers.core import BaseParser

__author__ = 'ilya'


class ItEventsParser(BaseParser):

    DEFAULT_ROOT_URL = 'http://it-events.com/'

    def search(self, search_string, limit, datetime_bounds=(None, None)):
        # TODO write code
        pass

    def get_one(self, url):
        # TODO write code
        pass

