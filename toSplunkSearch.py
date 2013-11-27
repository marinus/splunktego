#!/usr/bin/env python

"""
Copyright 2013 Marinus van Aswegen. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY MARINUS VAN ASWEGEN ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MARINUS VAN ASWEGEN OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Marinus van Aswegen.

"""

import time
import re
import requests
import sys
import os
import json
import MaltegoTransform as maltego

def get_api_key(**kw ):
	response = requests.post( kw['url'] + '/services/auth/login', 
		                      data={'username':kw['userid'], 'password':kw['passwd']},
		                      verify = kw['ssl_verify']) 

	if response.status_code != 200:
		return (response.status_code, None)
	else:
		key = re.findall('Key>([^<]+)',response.text)[0]
		return (response.status_code, key)

def search(**kw ):
	if not kw['search'].startswith('search'):
		kw['search'] = 'search ' + kw['search']

		job = requests.post(kw['url'] + '/services/search/jobs',
				            headers={'Authorization': 'Splunk %s' % kw['key']},
				            data={'search': kw['search']},
				            verify = kw['ssl_verify']) 

		try:
			sid = re.findall('sid>([^<]+)',job.text)[0]
			return (job.status_code, sid)
		except:
			return (job.status_code, None)

def get_status(**kw ):
	status = requests.get(kw['url'] + '/services/search/jobs/%s/' % sid,
		                  headers={'Authorization': 'Splunk %s' % kw['key']},
		                  verify = kw['ssl_verify'])                           

	if status.status_code == 200:
		done = re.findall('isDone">(0|1)', status.text)[0]

		if done == '1': 
			done = True
		else:
			done = False

		return (status.status_code, done)
	else:
		return (status.status_code, None)

def get_results(**kw ):
	results = requests.get( kw['url'] + '/services/search/jobs/%s/results?output_mode=json&count=0' % sid,
		                    headers={'Authorization': 'Splunk %s' % kw['key']},
		                    verify = kw['ssl_verify'])                                                       
	return (results.status_code, results.json()['results'])

if __name__ == '__main__':

	mt = maltego.MaltegoTransform()

	try:
		mt.debug('loading config')
		config = json.load(open('splunk.conf'))
		url = config['url']
		userid = config['userid']
		passwd = config['passwd']
		ssl_verify = config['ssl_verify']
	except Exception, msg:
		print msg.message
		sys.exit(-1)

	#mt.debug('values %s' % str(sys.argv))
	search_term = sys.argv[1] #'* | head 10 | fields source, _time'

	# parse out the fields
	try:
		fields = re.findall('fields(.*?)$', search_term)[0]
		fields = fields.split(',')
	except:
		mt.debug('no fields specified')
		sys.exit(-1)

	mt.debug('authenticating')
	(code, key) = get_api_key(url = url, 
		                      ssl_verify = ssl_verify, 
		                      userid = userid, 
		                      passwd = passwd)

	mt.debug('performing search')
	if str(code).startswith('20') and key:
		(code, sid) = search(url = url, 
				             ssl_verify = ssl_verify, 
				             key = key, 
				             search = search_term)

	mt.debug('waiting for job to finish')
	if str(code).startswith('20') and sid:
		count = 0
		while True:
			(code, status) = get_status(url = url, 
						                ssl_verify = ssl_verify, 
						                key = key, 
						                job = sid)
			if status:
				break

			if not str(code).startswith('20') or count > 10:
				print 'error ', code
				break

			count += 1
			time.sleep(0.5)

	mt.debug('requesting search results')
	if str(code).startswith('20') and status:
		(code, results) = get_results( url = url, 
				                       ssl_verify = ssl_verify, 
				                       key = key, 
				                       job = sid)
		if results:
			mt.debug('parsing results')
			for row in results:
				ent = mt.addEntity('unknown', row[fields[0].strip()])			
				for key in fields[1:]:
					ent.addAdditionalFields(key, key, True, row[key.strip()])
				
			mt.returnOutput()




