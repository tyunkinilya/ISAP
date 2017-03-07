# -*- coding: utf-8 -*-
"""
ISAP

Created by pavel on 24.02.17 18:13
"""

from bs4 import BeautifulSoup
import re
import time
import json
import stemmer
import requests
from core import BaseParser

__author__ = 'ilya'


class ItEventsParser(BaseParser):

    DEFAULT_ROOT_URL = 'http://it-events.com/'

    empty_event = {
            'link' : '',
            'category' : '',
            'site' : '',
            'info' : {'price' : '', 'dates' : '', 'geo' : '', 'contacts' : '', 'organizers' : ''},
            'anons_text' : '',
            'anons_keywords' : ''}

    def search(self, search_string = '', limit = 20, datetime_bounds = (None, None)):
        '''
        Возвращает список ссылок в формате '/events/[0-9]+'
        TODO:
        Разобраться с получением полного списка мероприятий по запросу (на странице используется javascript)
        '''

        html = requests.get(r'http://it-events.com/search?utf8=%E2%9C%93&full_search=false&q={0}&commit=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&city_name=&city_id='.format(search_string)).text
        soup = BeautifulSoup(html, 'html.parser').find('div', {'class' : 'event'})
        vevents = soup.findAll('div', {'class' : 'vevent'})
        events = []
        if limit > len(vevents):
            limit = len(vevents)
        for i in range(limit):
            events.append(vevents[i].find('h3').find('a').get('href')[1:])
        # self.write_event_txt(self.empty_event, 'output.txt', 'w')
        # for v in events:
        #     self.write_event_txt(self.get_one(self.root_path + v))


    def __check_connection(self, url):
        try:
            requests.get(url)
            return True
        except requests.exceptions.ConnectionError:
            return False

    def __get_html(self, url):
        return requests.get(url).text

    def __side_box_exist(self, aside, span_class):
        return True if aside.find('span', {'class' : span_class}) != None else False

    def __list_side_boxes(self, aside):
        side_boxes_classes = ['icon_card','icon_date','icon_geo','icon_user','icon_organizer']
        side_boxes_existance = [False]*5
        for i in range(5):
            side_boxes_existance[i] = self.__side_box_exist(aside, side_boxes_classes[i])
        return side_boxes_existance

    def __get_price(self, aside):
        return aside.find('div', {'class' : 'box_aside'}).find('p').text.strip().replace('[?]','')

    def __get_dates(self, aside):
        start_date = aside.findAll('strong', {'id' : "event_end_date"})[0].text.strip()
        end_date = aside.findAll('strong', {'id' : "event_end_date"})[1].text.strip()
        return {'start' : start_date, 'end' : end_date}

    def __get_geo(self, aside):
        region = aside.findAll('span', {'class' : "region"})[0]
        if region != None:
            region = region.text[1:-1].replace('\n', '')
        try:
            place = aside.findAll('span', {'class' : "region"})[1]
            if place != None:
                place = place.text[1:-1].replace('Место: ', '')
        except:
            place = None

        adress = aside.find('span', {'class' : 'street-adress'})
        if adress != None:
            adress = adress.text[1:-1]

        return {'region' : region, 'adress' : adress, 'place' : place}

    def __get_contacts(self, aside):
        if aside.find('a', {'href' : re.compile(r'/events/\d+\?contact')}) == None:
            contacts = aside.find('span', {'class' : 'icon_user'}).parent.nextSibling.nextSibling.findAll(re.compile('dd|dt'))
        else:
            contacts = aside.find('span', {'class' : 'icon_user'}).parent.parent.nextSibling.nextSibling.findAll(re.compile('dd|dt'))

        res = {'Имя': '', 'e-mail' : '', 'Телефон' : ''}
        for i in range(0, len(contacts), 2):
            res[contacts[i].text.replace('\n', '')] = contacts[i + 1].text.replace('\n', '')

        res['name'] = res.pop('Имя')
        res['tel_number'] = res.pop('Телефон')
        return res

    def __get_organizers(self, aside):
        organizers = aside.findAll('div', {'class' : 'box_aside organizer'})
        res = []
        for org in organizers:
            res.append(org.find('span').text.replace('\n', ''))
        return res

    def __get_category(self, soup):
        return soup.find('span', {'class' : 'category'}).a.text.replace('\n', '')

    def __get_event_site(self, soup):
        if soup.find('span', {'class' : 'fl_right'}).find('a') != None:
            return soup.find('span', {'class' : 'fl_right'}).find('a').get('href')
        else:
            return ''
    def __get_anons(self, soup):
        content = soup.find('article', {'class' : 'anons'})
        for x in content.findAll('img'):
            if x.get('src')[0] == '/':
                x['src'] = 'http://it-events.com' + x.get('src')
        return {'anons_text' : re.sub(r' +|\t+', ' ', re.sub(r'\n+', '\n', content.get_text())), 'anons_keywords' : stemmer.stem_text(content.get_text())}

    def __get_info(self, aside):
        
        event_info = {'price' : '', 'dates' : '', 'geo' : '', 'contacts' : '', 'organizers' : ''}
        
        side_boxes_existance = self.__list_side_boxes(aside)

        if side_boxes_existance[0]:
            event_info['price'] = self.__get_price(aside)

        if side_boxes_existance[1]:
            event_info['dates'] = self.__get_dates(aside)

        if side_boxes_existance[2]:
            event_info['geo'] = self.__get_geo(aside)

        if side_boxes_existance[3]:
            event_info['contacts'] = self.__get_contacts(aside)

        if side_boxes_existance[4]:
            event_info['organizers'] = self.__get_organizers(aside)

        return event_info

    def get_one(self, url):
        if self.__check_connection(url):
            html =  self.__get_html(url)
        else:
            print('Connection Error')
            return False
        soup = BeautifulSoup(html, 'html.parser')
        aside = soup.find('aside')
        anons = self.__get_anons(soup)
        if soup.find('h1', {'class' : 'msgError'}) == None:
            event = {
                    'link' : url,
                    'category' : self.__get_category(soup),
                    'site' : self.__get_event_site(soup),
                    'info' : self.__get_info(aside),
                    'anons_text' : anons['anons_text'],
                    'anons_keywords' : anons['anons_keywords']}
        else:
            event = self.empty_event
        return event

    def write_event_txt(self, event, path = 'output.txt', attr = 'a', an = 'text'):
        f = open(path, attr, encoding =  'utf-8')
        if event == self.empty_event:
            f.close()
            return False
        f.write('--------' + event['link'].replace(r'http://it-events.com/events/', '') + '--------' + '\n')
        f.write('category' + ' : ' + event['category'] + '\n')
        f.write('site' + ' : ' + event['site'] + '\n')
        for key, value in event['info'].items():
            f.write(str(key) + ' : ' + str(value) + '\n')
        f.write('--------ANONS-------' + '\n')
        f.write(event['anons_' + an] + '\n')
        f.close()

    def write_event_json(self, event, path, attr = 'a'):
        f = open(path, attr, encoding =  'utf-8')
        f.write(json.dumps(event))

if __name__ == '__main__':
    xxx = ItEventsParser()
    xxx.search(u'IT безопасность')
