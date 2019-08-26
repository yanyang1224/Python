# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib import parse
from bs4 import BeautifulSoup
import datetime
import random
import re
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

random.seed(datetime.datetime.now())
def getLinks(articleUrl):
    html = urlopen('http://zh.wikipedia.org{}'.format(parse.quote(articleUrl)))
    bs = BeautifulSoup(html,'html.parser')
    return bs.find('div',{'id':'bodyContent'}).find_all('a',href=re.compile('^(/wiki/)((?!:).)*$'))

links = getLinks('/wiki/凯文·贝肯')
while len(links) > 0:
    newArticle = links[random.randint(0,len(links)-1)].attrs['href']
    print(newArticle)
    links = getLinks(newArticle)