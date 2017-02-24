# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import requests
import re
import time
import json

def get_html(url):
	return requests.get(url).text

def side_box_exist(aside, span_class):
	return True if aside.find('span', {'class' : span_class}) != None else False

def list_side_boxes(aside):
	side_boxes_classes = ['icon_card','icon_date','icon_geo','icon_user','icon_organizer']
	side_boxes_existance = [False]*5
	for i in range(5):
		side_boxes_existance[i] = side_box_exist(aside, side_boxes_classes[i])
	return side_boxes_existance

def get_price(aside):
	return aside.find('div', {'class' : 'box_aside'}).find('p').text[1:-1].replace('[?]','').replace('\n', '')

def get_dates(aside):
	start_date = aside.findAll('strong', {'id' : "event_end_date"})[0].text[2:-1]
	end_date = aside.findAll('strong', {'id' : "event_end_date"})[1].text[2:-1]
	return {'start' : start_date, 'end' : end_date}

def get_geo(aside):
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

def get_contacts(aside):
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

def get_organizers(aside):
	organizers = aside.findAll('div', {'class' : 'box_aside organizer'})
	res = []
	for org in organizers:
		res.append(org.find('span').text.replace('\n', ''))
	return res

def get_category(soup):
	return soup.find('span', {'class' : 'category'}).a.text.replace('\n', '')

def get_event_site(soup):
	if soup.find('span', {'class' : 'fl_right'}).find('a') != None:
		return soup.find('span', {'class' : 'fl_right'}).find('a').get('href')
	else:
		return ''
def get_anons(soup):
	content = soup.find('article', {'class' : 'anons'})
	# return {'anons_html' : str(content), 'anons_text' : re.sub(r'\n+', '\n', content.get_text())}
	for x in content.findAll('img'):
		if x.get('src')[0] == '/':
			x['src'] = 'http://it-events.com' + x.get('src')
	return {'anons_html' : str(content), 'anons_text' : re.sub(r' +|\t+', ' ', re.sub(r'\n+', '\n', content.get_text()))}

def get_info(aside):
	functions_list = ['price', 'dates', 'geo', 'contacts', 'organizers']
	side_boxes_existance = list_side_boxes(aside)
	event_info = {'price' : '', 'dates' : '', 'geo' : '', 'contacts' : '', 'organizers' : ''}
	for i in range(len(functions_list)):
		if side_boxes_existance[i]:
			event_info[functions_list[i]] = eval('get_' + functions_list[i] + '(aside)')
	return event_info

def process_url(url):
	soup = BeautifulSoup(get_html(url), 'html.parser')
	aside = soup.find('aside')
	if soup.find('h1', {'class' : 'msgError'}) == None:
		event = {
				'link' : url,
				'category' : get_category(soup), 
				'site' : get_event_site(soup), 
				'info' : get_info(aside), 
				'anons' : get_anons(soup)}
	else:
		event = {
				'link' : url,
				'category' : '', 
				'site' : '', 
				'info' : {'price' : '', 'dates' : '', 'geo' : '', 'contacts' : '', 'organizers' : ''}, 
				'anons' : {'anons_html' : '', 'anons_text' : ''}}
	return event
	
def write_event_txt(event, path, attr = 'a'):
	f = open(path, attr, encoding =  'utf-8')
	f.write('--------' + event['link'].replace(r'http://it-events.com/events/', '') + '--------' + '\n')
	f.write('category' + ' : ' + event['category'] + '\n')
	f.write('site' + ' : ' + event['site'] + '\n')
	for key, value in event['info'].items():
		f.write(str(key) + ':' + str(value) + '\n')
	f.write('--------ANONS-------' + '\n')
	f.write(event['anons']['anons_text'] + '\n')
	# f.write('--------' + event['link'].replace(r'http://it-events.com/events/', '') + '--------' + '\n')

def write_event_json(event, path, attr = 'a'):
	f = open(path, attr, encoding =  'utf-8')
	f.write(json.dumps(event))

basic_url = 'http://it-events.com/events/'

event_num = 8715
write_event_txt(process_url(basic_url + str(event_num)), 'output.txt', 'w')
write_event_json(process_url(basic_url + str(event_num)), 'output.json', 'w')

# for event_num in range(8750,8751):
# 	print(event_num)
# 	write_event_txt(process_url(basic_url + str(event_num)), 'output.txt')
# 	write_event_json(process_url(basic_url + str(event_num)), 'output.json')
# 	time.sleep(4)