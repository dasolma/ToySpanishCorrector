#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib


def create_errors():
   cookie_jar = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
   urllib2.install_opener(opener)

   # acquire cookie
   url_1 = 'http://www.mystilus.com/'
   req = urllib2.Request(url_1)
   rsp = urllib2.urlopen(req)

   # do POST
   url_2 = 'http://www.mystilus.com/api/stilus'
   values = dict(key="stilusDemo2011", prod="web", txt="azaña", lang="es", ilang="es",
	      mode="next", iif="txt", of="json", offset="0", pp="y", tls="n", 
	      dpn="n", stme="2", red="y", spa="y", wps="y", psr="n", nsr="n",
              bsr="y", str="y", vr="y", sdm="y", ddm="y", comppunc="y", corrpunc="y",
              alw="y", wct="n", aqoi="y", dic="chetsdpqr")
   data = urllib.urlencode(values)
   req = urllib2.Request(url_2, data)
   rsp = urllib2.urlopen(req)
   content = rsp.read()


   print content

