#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import json
import xmltodict
from corrector import NWORDS
import random
from corrector import unknown_edits2, correct
import pickle
import os.path
import newspaper
from newspaper import Article
import datetime
import codecs
import dryscrape
from bs4 import BeautifulSoup
import requests
from lxml import html
import re
import corrector
import urllib
import pickle

import csv
from itertools import islice

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


def spelltest(tests, bias=None, verbose=False):
    import time
    n, bad, unknown, start = 0, 0, 0, time.clock()
    if bias:
        for target in tests: NWORDS[target] += bias

    for wrong, suggestions in tests.iteritems():

        print wrong
        words = correct(wrong.encode('utf-8'))

        n += 1

        for s in suggestions:
            if not s.decode('utf-8') in NWORDS:
                unknown += 1

        found = False;
        for w in words:
            print w['sug']
            if w['sug'] in suggestions:
                found = True

        if not found:
            bad += 1
            if verbose:
                print '%r => %r; expected %r ' % (
                    wrong, words, str(suggestions))

    return dict(bad=bad, n=n, bias=bias, pct=int(100. - 100.*bad/n),
                unknown=unknown, secs=int(time.clock()-start) )


def create_errors(file, iterations=1000):

    errors = {}

    if os.path.exists(file):
        errors = read_errors(file)

    for i in xrange(iterations):
        w = list(unknown_edits2(NWORDS.keys()[random.randint(0, len(NWORDS))]))
        w = w[random.randint(0, len(w))]

        sug = suggestings(w)

        if len(sug) > 0:
            errors[w] = sug

            if len(errors) % 10 == 0:
                save_errors(errors, file)

            print w + " :\t" + str(sug)

    save_errors(errors, file)

def save_errors(errors, file):
    with open(file, 'wb') as handle:
        pickle.dump(errors, handle)


def conjugations(f='../data/conjugations.p', verb=None):
    verbs = file('../data/verbos.txt').read().split('\n')
    verbs = [w.decode('utf-8') for w in verbs]
    session = dryscrape.Session()

    i = 0
    if verb != None:
        i = verbs.index(verb)


    try:
        data = pickle.load(open(f, 'rb'))
    except:
        data = {}

    for v in verbs[i:]:

        if not v in data:
            print v
            conj = conjugate(v.encode('utf-8'), session)

            if not conj is None and len(conj) > 0:
                data[v] = conj
                print len(data)
                print conj

                if len(data) % 10 == 0:
                    del session
                    session = dryscrape.Session()
                    pickle.dump(data, open(f, 'wb'))

                #myfile.write('\n'.join(conj))
                #myfile.write('\n')
            else:
                del session
                session = dryscrape.Session()


    return data

def conjugate(verb, session=None):
    if session is None:
        session = dryscrape.Session()
    BASE_URL = 'http://lema.rae.es/drae/srv/'
    SEARCH_URL = 'http://lema.rae.es/drae/srv/search?val='

    try:
        verb = urllib.quote(verb.decode('utf-8').encode('iso-8859-1'))

        session.visit(SEARCH_URL+verb)
        response = session.body()
        tree = html.fromstring(response)
        #take the button link

        words = []
        conj_url = tree.xpath("//img[@alt='Ver conjugación']/..".decode('latin1'))[0].attrib['href']

        session.visit(BASE_URL+conj_url)
        response = session.body()
        print response
        tree = html.fromstring(response.replace('<br>', " / "))

        words = [ re.split('/ | o', y) for y in [x.text_content() for x in tree.xpath("//p[@class='z']")]]
        words = [item.encode('latin1').decode('utf-8').strip() for sublist in words for item in sublist if len(item.strip()) > 0]
        words = [re.split(' ', y) for y in words]
        words = [item for sublist in words for item in sublist if len(item.strip()) > 1]
        words = [item.replace(',', '') for item in words if not item in ('se', 'os', 'nos', 'te', 'me','etc.')]
    except Exception as ex:
        print ex
        pass



    return words

def valid(word, session=None):
    if session is None:
        session = dryscrape.Session()
    SEARCH_URL = 'http://lema.rae.es/drae/srv/search?val='

    try:
        verb = urllib.quote(word.decode('utf-8').encode('iso-8859-1'))
        session.visit(SEARCH_URL+verb)


        print session.body()
        return not 'registrada' in session.body()


    except Exception as ex:
        print ex
        return False



def read_errors(file):
    return pickle.load(open(file, "rb"))



def suggestings(word):
    cookie_jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    urllib2.install_opener(opener)

    # acquire cookie
    url_1 = 'http://www.correctorortografico.com'
    req = urllib2.Request(url_1)
    rsp = urllib2.urlopen(req)

    # do POST
    url_2 = 'http://www.correctorortografico.com/motor.php?lang=es'

    print word
    data = u'<?xml version="1.0" encoding="utf-8" ?><spellrequest textalreadyclipped="0" ignoredups="0" ignoredigits="1" ignoreallcaps="1"><text>'+word+u'</text></spellrequest>'

    sug = []
    try:
        req = urllib2.Request(url_2, data.encode('utf-8'),  {'Content-type': 'text/xml; charset=utf-8'})

        rsp = urllib2.urlopen(req)

        xml = xmltodict.parse(rsp.read())['spellresult']


        if 'c' in xml and '#text' in xml['c']:
            sug = xml['c']['#text'].split('\t')

        #content = json.loads(rsp.read())


        #sug = list([ x['form'] for x in content["result_list"][0]["sug_list"]])
        sug = [x.encode('utf-8') for x in sug]
    except:
        pass


    return sug

def news_scrapper(file = '../data/news.txt'):
    visited = set([])

    current_date = datetime.date(2011, 1, 2)
    finish_date = datetime.date(2015, 1, 1)

    while( current_date < finish_date ):
        c = current_date
        url = 'http://www.elmundo.es/elmundo/hemeroteca/'+ str(c.year) +'/' + '%02d' % c.month +'/'+ '%02d' % c.day +'/m/'
        print url
        paper = newspaper.build(url, language="es", memoize_articles=False)

        urls = set([l.url for l in paper.articles])
        urls = urls - visited
        visited = visited or urls

        for url in urls:
            print url
            article = Article(url, language="es", fetch_images=False)
            article.download()
            article.parse()

            if len(article.text) > 200:

                with codecs.open(file, "a", "utf-8") as myfile:
                    myfile.write(article.text)



        current_date  += datetime.timedelta(days=1)




def create_errors_old(word):
   cookie_jar = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
   urllib2.install_opener(opener)

   # acquire cookie
   url_1 = 'http://www.mystilus.com/'
   req = urllib2.Request(url_1)
   rsp = urllib2.urlopen(req)

   # do POST
   url_2 = 'http://www.mystilus.com/api/stilus'
   values = dict(key="stilusDemo2011", prod="web", txt=word, lang="es", ilang="es",
	      mode="next", iif="txt", of="json", offset="0", pp="y", tls="n",
	      dpn="n", stme="2", red="y", spa="y", wps="y", psr="n", nsr="n",
              bsr="y", str="y", vr="y", sdm="y", ddm="y", comppunc="y", corrpunc="y",
              alw="y", wct="n", aqoi="y", dic="chetsdpqr")
   data = urllib.urlencode(values)
   req = urllib2.Request(url_2, data)
   rsp = urllib2.urlopen(req)
   content = json.loads(rsp.read())


   sug = list([ x['form'] for x in content["result_list"][0]["sug_list"]])
   sug = [x.encode('utf-8') for x in sug]

   return sug

#print spelltest(tests1)
#print spelltest(tests2) ## only do this after everything is debugged
