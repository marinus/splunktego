"""
splunktego (marinus@telic.co.za)

Examples

  | maltego file=/tmp/export1 type=IP e1=src e2=dst label=port 
  | maltego file=/tmp/export1 type=IP e1=src e2=dst 
  | maltego file=/tmp/export1 type=IP e1=src


You can test the script from the CLI using 
splunk cmd python maltego.py

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

import splunk.Intersplunk
import sys
import math
import os
import tempfile
import pymtgx
import posixpath

DEBUG = True # write debug info out
entities_file = "/opt/splunk/etc/apps/splunktego/bin/entities.mtz"

def log(msg):
	if DEBUG:
		open('/tmp/maltego.debug.log','a').write(msg)

def is_safe(fname):
	if os.path.islink(fname):
		return False, 'symlinks not supported'
	
	path = posixpath.normpath(fname)
	if not path.startswith(('/home', '/tmp')):
		return False, 'you can only write to /home or /tmp'
	
	if path.count('.') > 0:
		return False, 'mmmm what are you doing?'
	
	return True, None


try:
	# get the params
	keywords,options = splunk.Intersplunk.getKeywordsAndOptions()
	log('keywords=%s,options=%s\n' % (keywords,options))
	
	# parse the params
	e1 = options.get('e1', None)
	e2 = options.get('e2', None)
	label = options.get('label', None)
	fname = options.get('file', None)
	etype = options.get('type', 'Phrase')
	
	if not e1:
		splunk.Intersplunk.generateErrorResults("must specify at least one entity")
		exit(0)		
	
	if not fname:
		splunk.Intersplunk.generateErrorResults("must specify the destination file")
		exit(0)		
		
	safe, msg = is_safe(fname)
	if not safe:
		splunk.Intersplunk.generateErrorResults(msg)
		exit(0)		
		
	
	mtgx = pymtgx.Pymtgx()
	mtgx.register_entities(entities_file)		
		
	# get the previous search results
	results,unused1,unused2 = splunk.Intersplunk.getOrganizedResults()

	nodes = {}
	links = []

	# parse the results
	for result in results:
		nodes[result[e1]] = True
		if e2: 
			nodes[result[e2]] = True
		
		if label:
			links.append((result[e1],result[e2],result.get(label,'?')))
			
	# create the graph
	if not e2:
		# create nodes
		for node in nodes:
			mtgx.add_node("maltego." + etype , node)
	else:
		# create nodes
		for node in nodes:
			nodes[node] = mtgx.add_node("maltego." + etype , node)
			
		# create relationships
		for (e1,e2,label) in links:
			mtgx.add_edge(nodes[e1], nodes[e2], label)

	# zero out the response
	results = []
	
	# output results
	splunk.Intersplunk.outputResults(results)

	# write the graph
	mtgx.create(fname)
	
except Exception, e:
	results = splunk.Intersplunk.generateErrorResults(str(e))


