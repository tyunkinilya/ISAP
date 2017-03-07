# -*- coding: utf-8 -*-
"""
TODO About
"""

import re

class Porter:
    perfectiveground =  re.compile("((ив|ивши|ившись|ыв|ывши|ывшись)|((?<=[ая])(в|вши|вшись)))$")
    reflexive = re.compile("(с[яь])$")
    adjective = re.compile("(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|ую|юю|ая|яя|ою|ею)$")
    participle = re.compile("((ивш|ывш|ующ)|((?<=[ая])(ем|нн|вш|ющ|щ)))$")
    verb = re.compile("((ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|ыло|ено|ят|ует|уют|ит|ыт|ены|ить|ыть|ишь|ую|ю)|((?<=[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|нно)))$")
    noun = re.compile("(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я)$")
    rvre = re.compile("^(.*?[аеиоуыэюя])(.*)$")
    derivational = re.compile(".*[^аеиоуыэюя]+[аеиоуыэюя].*ость?$")
    der = re.compile("ость?$")
    superlative = re.compile("(ейше|ейш)$")
    i = re.compile("и$")
    p = re.compile("ь$")
    nn = re.compile("нн$")

    def stem(word):
        word = word.lower()
        word = word.replace('ё', 'е')
        m = re.match(Porter.rvre, word)
        if m == None:
            return word
        if m.groups():
            pre = m.group(1)
            rv = m.group(2)
            temp = Porter.perfectiveground.sub('', rv, 1)
            if temp == rv:
                rv = Porter.reflexive.sub('', rv, 1)
                temp = Porter.adjective.sub('', rv, 1)
                if temp != rv:
                    rv = temp
                    rv = Porter.participle.sub('', rv, 1)
                else:
                    temp = Porter.verb.sub('', rv, 1)
                    if temp == rv:
                        rv = Porter.noun.sub('', rv, 1)
                    else:
                        rv = temp
            else:
                rv = temp
            
            rv = Porter.i.sub('', rv, 1)

            if re.match(Porter.derivational, rv):
                rv = Porter.der.sub('', rv, 1)

            temp = Porter.p.sub('', rv, 1)
            if temp == rv:
                rv = Porter.superlative.sub('', rv, 1)
                rv = Porter.nn.sub(u'н', rv, 1)
            else:
                rv = temp
            word = pre+rv
        return word
    stem = staticmethod(stem)

def stem_phrase(phrase):
    res = list(phrase.lower().split())
    for i in range(len(res)):
        res[i] = Porter.stem(res[i])
    return res


def stem_text(text):
    text = re.sub(r'\W|\d', ' ', text).lower()
    # TODO в отдельный список, затем '| '.join(...)
    text = re.sub(r' й | - | а | без | более | больше | будет | будто | бы | был | была | были | было | быть | в | вам | вас | вдруг | ведь | во | вот | впрочем | все | всегда | всего | всех | всю | вы | г | где | говорил | да | даже | два | для | до | другой | его | ее | ей | ему | если | есть | еще | ж | же | жизнь | за | зачем | здесь | и | из | из-за | или | им | иногда | их | к | кажется | как | какая | какой | когда | конечно | которого | которые | кто | куда | ли | лучше | между | меня | мне | много | может | можно | мой | моя | мы | на | над | надо | наконец | нас | не | него | нее | ней | нельзя | нет | ни | нибудь | никогда | ним | них | ничего | но | ну | о | об | один | он | она | они | опять | от | перед | по | под | после | потом | потому | почти | при | про | раз | разве | с | сам | свое | свою | себе | себя | сегодня | сейчас | сказал | сказала | сказать | со | совсем | так | такой | там | тебя | тем | теперь | то | тогда | того | тоже | только | том | тот | три | тут | ты | у | уж | уже | хорошо | хоть | чего | человек | чем | через | что | чтоб | чтобы | чуть | эти | этого | этой | этом | этот | эту | я ', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    uniq = []
    for word in stem_phrase(text):
        if not word in uniq:
            uniq.append(word)

    return ' '.join(uniq)

if __name__ == '__main__':
    # print(*stem_phrase(input('Phrase: ')))
    
    text = '''
    '''
    with open('stem_output.txt', 'w', encoding='utf-8') as f:
        f.write(stem_text(text))
