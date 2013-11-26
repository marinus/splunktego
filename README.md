splunktego (@marinusva)
==============
Collections of tools to make Splunk and Maltego play nice.

There's two primary modes.

1. Sending entities to Maltego, via a new splunk search command (splunk2maltego)
2. Searching for entities from Maltego, using a transform (maltego2splunk)


S2M Examples
--------------
syntax
* | maltego e1=entity [e2=entity] [type=entity type] [label=label] file=file name

export a list of entities
* | maltego e1=src type=IPv4Address file=/tmp/attack

export related entities
* | maltego e1=src e2=dst label=proto type=IPv4Address file=/tmp/attacks


M2S Examples
--------------
create a Phrase entity
"earliest=-1d source=fwlogs | dedup ip | fields ip"
call the to SplunkSearch transform 



S2M Installation
--------------
Important read this carefully.
Splunk maintains its own Python installation, which makes it hard to install 3rd party modules.
To simplify matters and not break Splunk, pymtgx and networkx dependencies need to be symlinked into the splunk apps' bin directory.
Following the sagely advice of the Sorkin, http://answers.splunk.com/answers/6033/adding-python-module-to-splunk

1. Clone the two packages from github
2. Link to the source from splunk/etc/apps
   cd <where you installed splunk/etc/apps/splunktego
   ln -s .../networkx/networkx .
   ln -s .../pymtgx/pymtgx.py .

pymtx, requires an extract of entities from Maltego. 
Export them, and update the path in the maltogo.py file.


Credits
--------------
Petter Christian Bjelland for pymtgx
