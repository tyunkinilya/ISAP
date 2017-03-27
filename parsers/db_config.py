# -*- coding: utf-8 -*-

from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.orm import mapper
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