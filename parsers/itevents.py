# -*- coding: utf-8 -*-
"""
ISAP

Created by pavel on 24.02.17 18:13
"""

from core import BaseParser

from bs4 import BeautifulSoup
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, mapper

import sys
import re
import time
import json
import stemmer
import requests

import configparser

__author__ = 'ilya'


'''
Class and table for db
'''
metadata = MetaData()
events_table = Table('events', metadata,
    Column('event_id', Integer, primary_key=True, autoincrement=True),
    Column('link', String),
    Column('category', String),
    Column('site', String),
    Column('price', String),
    Column('start_date', String),
    Column('end_date', String),
    Column('region', String),
    Column('adress', String),
    Column('place', String),
    Column('name', String),
    Column('tel_number', String),
    Column('email', String),
    Column('organizers', String),
    Column('anons_text', String),
    Column('anons_keywords', String),
    Column('class_IS', Integer)
)

class itevent(object):
    def __init__(self, link, category, site, price, start_date, end_date, region, adress, place, name, tel_number, email, organizers, anons_text, anons_keywords, class_IS):
        self.link = link
        self.category = category
        self.site = site
        self.price = price
        self.start_date = start_date
        self.end_date = end_date
        self.region = region
        self.adress = adress
        self.place = place
        self.name = name
        self.tel_number = tel_number
        self.email = email
        self.organizers = organizers
        self.anons_text = anons_text
        self.anons_keywords = anons_keywords
        self.class_IS = class_IS

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (self.event_id, self.link, self.category, self.site, self.price, self.start_date, self.end_date, self.region, self.adress, self.place, self.name, self.tel_number, self.email, self.organizers, self.anons_text, self.anons_keywords, self.class_IS)

mapper(itevent, events_table)

'''
Main class
'''

class ItEventsParser(BaseParser):

    DEFAULT_ROOT_URL = 'http://it-events.com/'

    empty_event = {
            'link' : '',
            'category' : '',
            'site' : '',
            'info' : {'price' : '', 'dates' : '', 'geo' : {'region' : '', 'adress' : '', 'place' : ''}, 'contacts' : {'name': '', 'e-mail' : '', 'tel_number' : ''}, 'organizers' : ''},
            'anons_text' : '',
            'anons_keywords' : ''}

    def search(self, search_string = '', limit = 20, datetime_bounds = (None, None)):
        '''
        Возвращает список ссылок в формате 'events/[0-9]+'
        '''

        html = requests.get(r'http://it-events.com/search?utf8=%E2%9C%93&full_search=false&q={0}&commit=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&city_name=&city_id='.format(search_string)).text
        soup = BeautifulSoup(html, 'html.parser').find('div', {'class' : 'event'})
        vevents = soup.findAll('div', {'class' : 'vevent'})
        events = []
        if limit > len(vevents):
            limit = len(vevents)
        for i in range(limit):
            events.append(vevents[i].find('h3').find('a').get('href')[1:])
        return events

    def __check_connection(self, url):
        try:
            requests.get(url)
            return True
        except requests.exceptions.ConnectionError:
            return False

    def __check_event_exist(self, url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        return True if soup.find('h1', {'class' : 'msgError'}) == None else False

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

    def __conv_datetime(self, s):
        months = {
              'января' : '01',
              'февраля' : '02',
              'марта' : '03',
              'апреля' : '04',
              'мая' : '05',
              'июня' : '06',
              'июля' : '07',
              'августа' : '08',
              'сентября' : '09',
              'октября' : '10',
              'ноября' : '11',
              'декабря' : '12',
              }
        if s != '':
            dt = s.split()
            res = dt[2] + '-' + months[dt[1]] + '-'
            if len(dt[0]) == 1:
              res += '0' + dt[0]
            else:
              res += dt[0]
            res += ' ' + dt[4] + ':00'
            return res
        else:
            return ''

    def __get_dates(self, aside):
        start_date = aside.findAll('strong', {'id' : "event_end_date"})[0].text.strip()
        end_date = aside.findAll('strong', {'id' : "event_end_date"})[1].text.strip()
        return {'start' : self.__conv_datetime(start_date), 'end' : self.__conv_datetime(end_date)}

    def __get_geo(self, aside):
        region = aside.findAll('span', {'class' : "region"})[0]
        if region != None:
            region = region.text[1:-1].replace('\n', '')
        else:
            region = ''

        try:
            place = aside.findAll('span', {'class' : "region"})[1]
            if place != None:
                place = place.text[1:-1].replace('Место: ', '')
        except:
            place = ''

        adress = aside.find('span', {'class' : 'street-adress'})
        if adress != None:
            adress = adress.text[1:-1]
        else:
            adress = ''

        return {'region' : region, 'adress' : adress, 'place' : place}

    def __get_contacts(self, aside):
        if aside.find('a', {'href' : re.compile(r'/events/\d+\?contact')}) == None:
            contacts = aside.find('span', {'class' : 'icon_user'}).parent.nextSibling.nextSibling.findAll(re.compile('dd|dt'))
        else:
            contacts = aside.find('span', {'class' : 'icon_user'}).parent.parent.nextSibling.nextSibling.findAll(re.compile('dd|dt'))

        res = {'Имя': '', 'e-mail' : '', 'Телефон' : ''}
        for i in range(0, len(contacts), 2):
            res[contacts[i].text.replace('\n', '')] = contacts[i + 1].text.replace('\n', '').strip()

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
        return {'anons_text' : re.sub(r' +|\t+', ' ', re.sub(r'\n+', '\n', content.get_text())).strip(), 'anons_keywords' : stemmer.stem_text(content.get_text())}

    def __get_info(self, aside):
        event_info = {'price' : '', 'dates' : '', 'geo' : {'region' : '', 'adress' : '', 'place' : ''}, 'contacts' : {'name': '', 'e-mail' : '', 'tel_number' : ''}, 'organizers' : ''}
        
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
            event_info['organizers'] = '; '.join(self.__get_organizers(aside))

        return event_info

    def get_one(self, url):
        if self.__check_connection(url):
            html =  self.__get_html(url)
        else:
            print('Connection Error')
            return False
        soup = BeautifulSoup(html, 'html.parser')
        aside = soup.find('aside')
        if self.__check_event_exist(url):
            anons = self.__get_anons(soup)
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

    def add_to_db(self, events, path = 'sqlite:///events.db'):
        db = create_engine(path)
        metadata.create_all(db)
        Session = sessionmaker(bind = db)
        session = Session()
        n = len(events)
        new_ev = 0
        for i in range(n):
            ev = self.get_one(self.root_path + events[i])
            if ev != self.empty_event:
                event_in_db = session.execute(events_table.select().where(events_table.c.link == ev['link'])).first()
                if event_in_db == None:
                    event = itevent(ev['link'], ev['category'], ev['site'], ev['info']['price'], ev['info']['dates']['start'], ev['info']['dates']['end'], ev['info']['geo']['region'], ev['info']['geo']['adress'], ev['info']['geo']['place'], ev['info']['contacts']['name'], ev['info']['contacts']['tel_number'], ev['info']['contacts']['e-mail'], ev['info']['organizers'], ev['anons_text'], ev['anons_keywords'], None)
                    session.add(event)
                    new_ev += 1
            sys.stdout.write('\rAdding to database: {:.2%}'.format((i + 1) / n))
            sys.stdout.flush()
        print('\nAdded {} new events'.format(new_ev))
        session.commit()
        return True

    def check_updates(self):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        last_event_id = int(config.get('itevents', 'last_event_id'))
        check_step = int(config.get('itevents', 'step'))
        new_max = last_event_id
        buff = []
        for i in range(last_event_id + 1, last_event_id + check_step + 2):
            if self.__check_event_exist(self.root_path + 'events/' + str(i)):
                buff.append('events/' + str(i))
                new_max = i
            sys.stdout.write('\rChecking for updates: {:.2%}'.format((i - last_event_id - 1) / check_step))
            sys.stdout.flush()
        print()
        if buff:
            self.add_to_db(buff)
            config.set('itevents', 'last_event_id', str(new_max))
            with open('config.cfg', 'w') as configfile:
                config.write(configfile)
            self.check_updates()
        else:
            print('No new events')
        return True


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
    xxx = ItEventsParser().check_updates()