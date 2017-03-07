# -*- coding: utf-8 -*-
"""
ISAP
core

Ядро модуля parsers.
Содержит:
  * псевдоабстрактный клас BaseParser

Created by pavel on 24.02.17 18:02
Edited by Ilya on 25.02.17 2:10
"""
import datetime
import requests

__authors__ = ['pavel', 'ilya']


DEFAULT_SEARCH_DEPTH = datetime.timedelta(hours=2)


class BaseParser:
    """
    Базовый псеводоабстрактный класс.
    """

    # root_path по умолчанию
    DEFAULT_ROOT_URL = None

    def __init__(self, root_url=None):
        if self.DEFAULT_ROOT_URL is None:
            raise NotImplemented('Не указан DEFAULT_ROOT_URL')
        if root_url:
            self.root_path = root_url
        else:
            self.root_path = self.DEFAULT_ROOT_URL

    def __fix_datetime_bounds(self, datetime_bounds):
        datetime_bounds = list(datetime_bounds)
        if datetime_bounds[1] is None:
            datetime_bounds[1] = datetime.datetime.now()
        if datetime_bounds[0] is None:
            datetime_bounds[0] = datetime_bounds[1] - DEFAULT_SEARCH_DEPTH
        return datetime_bounds

    def search(self, search_string, limit, datetime_bounds=(None, None)):
        """
        Функция, возвращающая список url-ов, релевантные запросу.
        :param search_string: строка для поиска
        :param limit: максимальное количество возвращаемых значений поиска
        :param datetime_bounds: времена валидности для поиска.
        :return:
            список url-ов
        """
        datetime_bounds = self.__fix_datetime_bounds(datetime_bounds)

        raise NotImplemented()

    # TODO дописать описание
    def get_one(self, url):
        """
        возвращает информацию по одному url
        :param url:
        :return:
        словарь:
            category
            site
            price
            dates
            geo:
            contacts:
            organizers:
            short_anons: короткий анонс
            long_anons: длинный анонс
        """
        raise NotImplemented()

    def __str__(self):
        return "{0}<{1}>".format(self.__class__.__name__, self.root_path)



