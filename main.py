# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import requests

url = 'http://it-events.com/events/7000'

def get_html(url):
	return requests.get(url).text

def side_box_exist(aside, span_class):
	return True if aside.find('span', {'class' : span_class}) != None else False

def list_side_boxes(aside):
	side_boxes_classes = ['icon_card','icon_date','icon_geo','icon_translation','icon_user','icon_socials','icon_event_group','icon_organizer','icon_sponsor','icon_partner','icon_registered']
	side_boxes_existance = [False]*11
	for i in range(11):
		side_boxes_existance[i] = side_box_exist(aside, side_boxes_classes[i])
	return side_boxes_existance

def get_price(aside):
	return aside.find('div', {'class' : 'box_aside'}).find('p').text[1:-1].replace('\n[?]','')

def get_dates(aside):
	start_date = soup.findAll('strong', {'id' : "event_end_date"})[0].text[2:-1]
	end_date = soup.findAll('strong', {'id' : "event_end_date"})[1].text[2:-1]
	return [start_date, end_date]

def get_geo(aside):
	region = soup.findAll('span', {'class' : "region"})[0]
	if region != None:
		region = region.text[1:-1].replace('\n', '')

	place = soup.findAll('span', {'class' : "region"})[1]
	if place != None:
		place = place.text[1:-1].replace('Место: ', '')

	adress = soup.find('span', {'class' : 'street-adress'})
	if adress != None:
		adress = adress.text[1:-1]

	return [region, adress, place]

soup = BeautifulSoup(get_html(url), 'html.parser')

aside = soup.find('aside')
# num_boxes = len(aside.findAll('div', {'class' : 'box_aside'}))
side_boxes_existance = list_side_boxes(aside)
# print(num_boxes)
print(side_boxes_existance)