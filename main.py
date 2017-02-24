# -*- coding: UTF-8 -*-
import itevents
import stemmer

basic_url = 'http://it-events.com/events/'

event_num = 8522
event = itevents.process_url(basic_url + str(event_num))
itevents.write_event_txt(event, 'output.txt', 'w')
# itevents.write_event_json(event, 'output.json', 'w')


def find_phrase(phrase, event):
    ph = stemmer.stem_phrase(phrase)
    res = 0
    for word in ph:
        if not event['anons']['anons_keywords'].find(word) == -1:
            res += 1
    return res if res == 0 else res / len(ph)

print(find_phrase('Информационная безопасность', event))