# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import requests
import re
import time

basic_url = 'http://it-events.com/events/'

def get_html(url):
	return requests.get(url).text

def side_box_exist(aside, span_class):
	return True if aside.find('span', {'class' : span_class}) != None else False

def list_side_boxes(aside):
	# side_boxes_classes = ['icon_card','icon_date','icon_geo','icon_translation','icon_user','icon_socials','icon_event_group','icon_organizer','icon_sponsor','icon_partner','icon_registered']
	# side_boxes_existance = [False]*11
	# for i in range(11):
	# 	side_boxes_existance[i] = side_box_exist(aside, side_boxes_classes[i])
	# return side_boxes_existance

	side_boxes_classes = ['icon_card','icon_date','icon_geo','icon_user']
	side_boxes_existance = [False]*4
	for i in range(4):
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
	try:
		place = soup.findAll('span', {'class' : "region"})[1]
		if place != None:
			place = place.text[1:-1].replace('Место: ', '')
	except:
		place = None

	adress = soup.find('span', {'class' : 'street-adress'})
	if adress != None:
		adress = adress.text[1:-1]

	return [region, adress, place]

def get_contacts(aside):
	if soup.find('a', {'href' : re.compile(r'/events/\d+\?contact')}) == None:
		contacts = soup.find('span', {'class' : 'icon_user'}).parent.nextSibling.nextSibling
	else:
		contacts = soup.find('span', {'class' : 'icon_user'}).parent.parent.nextSibling.nextSibling

	name = re.compile(r'([А-Яа-я]+)').findall(str(contacts))
	if len(name) == 3:
		name = name[1]
	else:
		name = None

	email = contacts.find('a')
	if email != None:
		email = email.get('href').replace('mailto:', '')

	tel_number = contacts.find(text=re.compile(r'(\+ *\d{1,3} *\(\d{1,3}\) *(\d{1,3}[- ]*)*)|(\d+)'))
	if tel_number != None:
		tel_number = tel_number.replace('\n', '')
	return [name, email, tel_number]

functions_list = ['get_price(aside)', 'get_dates(aside)', 'get_geo(aside)', 'get_contacts(aside)']

# 8010 - error

for j in range(8010, 8050):
	soup = BeautifulSoup(get_html(basic_url + str(j)), 'html.parser')
	aside = soup.find('aside')

	side_boxes_existance = list_side_boxes(aside)

	event_info = [None]*4

	for i in range(4):
		if side_boxes_existance[i]:
			event_info[i] = eval(functions_list[i])

	print('\n--------' + str(j) + '--------\n')
	print(*event_info, sep='\n')
	print('\n--------' + str(j) + '--------\n')

	time.sleep(5)