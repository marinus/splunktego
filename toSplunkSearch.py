#!/usr/bin/env python

import time
import re
import requests
import sys
import os

def get_api_key(**kw):
    response = requests.post( kw['url'] + '/services/auth/login', 
                          data={'username':kw['userid'], 'password':kw['passwd']},
                          verify = kw['ssl_verify']) 

    if response.status_code != 200:
        return (response.status_code, None)
    else:
        key = re.findall('Key>([^<]+)',response.text)[0]
        return (response.status_code, key)
    
def search(**kw):
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
        
def get_status(**kw):
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

def get_results(**kw):
    results = requests.get( kw['url'] + '/services/search/jobs/%s/results?output_mode=json&count=0' % sid,
                            headers={'Authorization': 'Splunk %s' % kw['key']},
                            verify = kw['ssl_verify'])                                                       
    return (results.status_code, results.json()['results'])

if __name__ == '__main__':
    
    url = 'https://localhost:8089'
    userid = 'admin'
    passwd = '123456'
    ssl_verify = False    
    
    search_term = '* | head 10 | fields source, _time'
    
    # parse out the fields
    try:
        fields = re.findall('fields(.*?)$', search_term)[0]
        fields = fields.split(',')
    except:
        print 'no fields specified'
        sys.exit(-1)
    
    (code, key) = get_api_key(url = url, 
                              ssl_verify = ssl_verify, 
                              userid = userid, 
                              passwd = passwd)
    
    if str(code).startswith('20') and key:
        (code, sid) = search(url = url, 
                             ssl_verify = ssl_verify, 
                             key = key, 
                             search = search_term)
    
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
            
    if str(code).startswith('20') and status:
        (code, results) = get_results( url = url, 
                                     ssl_verify = ssl_verify, 
                                     key = key, 
                                     job = sid)
        for row in results:
            for key in fields:
                print row[key.strip()],
            print '\n'
        
    
            
            
            