# -*- coding: UTF-8 -*-
import itevents

basic_url = 'http://it-events.com/events/'

event_num = 8750
event = itevents.process_url(basic_url + str(event_num))
itevents.write_event_txt(event, 'output.txt', 'w')
itevents.write_event_json(event, 'output.json', 'w')
print(str(itevents.event_to_json(event)))