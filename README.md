splunktego (@marinusva)
==============

Make Splunk and Maltego play nice.
You'd probbable what to
  send entities to Maltego from Splunk, via a new splunk search command (splunk2maltego), or
  search for entities via Splunk from Maltego, using a transform (maltego2splunk)


S2M Examples
--------------
syntax
```
* | maltego e1=entity [e2=entity] [type=entity type] [label=label] file=filename
```
export a list of entities
```
* | maltego e1=src type=IPv4Address file=/tmp/attack
```
export entities with relationships
```
* | maltego e1=src e2=dst label=proto type=IPv4Address file=/tmp/attacks
```
for all the systems that are being splunked,
   find all ip addresses, accross all the logs,
   send to malto a deduplicated list of host to ip address relationships,
   indicating when the last event was received.
   Phew!
```
* | rex "(?<ip_address>\b\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\b)" | dedup ip_address, host | convert ctime(_time) as time | maltego e1=ip_address e2=host label=time file=/tmp/whostalking
```

You can not load these graphs in Maltego.

Limit your search result, so that you don't overflow Maltego.


M2S Examples
--------------

I want a list of IP Addresses that have been seen by splunk.

Add a Splunk search as a Phrase.
```
"* | rex "(?<ip_address>\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)" | dedup ip_address | fields ip_address, _time, source"
```  

select the "to Splunk Search" transform
Profit!

Enter your splunk search
"earliest=-1d source=fwlogs | dedup ip | fields ip"
call the to SplunkSearch transform 

The transform will connect to a splunk indexer, perform the search and parse the results.
It will create an entity using the first fields specified i.e. ip_address, additional fields will be added to the entity as attributes.

You must end your search with the fields command!
Limit your search result, so that you don't overflow Maltego.


Installation
--------------
Important read this carefully.

1. Copy the splunktego Splunk App to <where you installed splunk/etc/apps/

Splunk maintains its own Python installation, which makes it hard to install 3rd party modules.
To simplify matters and not break Splunk, pymtgx and networkx dependencies need to be symlinked into the splunk apps' bin directory.
Following the sagely advice of the Sorkin, http://answers.splunk.com/answers/6033/adding-python-module-to-splunk

- Clone the pymtgx and networkx from github
  https://github.com/networkx/networkx.git
  https://github.com/pcbje/pymtgx.git
  
- Link to the source from splunk/etc/apps/splunktego/bin
  cd <where you installed splunk/etc/apps/splunktego/bin
  ln -s .../networkx/networkx .
  ln -s .../pymtgx/src/pymtgx.py .
  
  
  

pymtx, requires an extract of entities from Maltego. 
Export them, and update the path in the maltogo.py file.
A default has been provided.

2. Create a new local transform

Point to the "toSplunkSearch.py" file.
Make sure the working directory points to where you installed it.


Thanks to Petter Christian Bjelland for pymtgx, and AndrewM for his Maltego module
