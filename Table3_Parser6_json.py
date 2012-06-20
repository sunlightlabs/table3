#Table 3 Parser
#United States Code: Table of Classifications for Public Laws
#Alex Engler
#Sunlight Foundation


##SCRAPER

import urllib2
from lxml import etree
from lxml.cssselect import CSSSelector
import cStringIO as StringIO
from sys import argv


congress_session = argv[1]

html_parser = etree.HTMLParser()

url1 = "http://uscodebeta.house.gov/classification/tbl" + congress_session + "pl_1st.htm"
url2 = "http://uscodebeta.house.gov/classification/tbl" + congress_session + "pl_2nd.htm"

connection1 = urllib2.urlopen(url1)
page_content1 = connection1.read()
page1 = etree.parse(StringIO.StringIO(page_content1), html_parser)
tag_content1 = CSSSelector('.page_content_internal pre font')(page1)[0]
full_content1 = tag_content1.text.strip()

connection2 = urllib2.urlopen(url2)
page_content2 = connection2.read()
page2 = etree.parse(StringIO.StringIO(page_content2), html_parser)
tag_content2 = CSSSelector('.page_content_internal pre font')(page2)[0]
full_content2 = tag_content2.text.strip()


##PARSER

import re
from collections import OrderedDict
import json

EXPRESSIONS = {
	'usc_title': '(^[*]{1,2}\d\d?A?)|(^\d\d?A?)',
	#usc_title regex notes: The first option is in case of an asterisk before the title number, the second option is the norm.
	'usc_section': '[ ]\d{1,5}\w*-?\w*',
	'public_law_number': '\d{1,3}-\d{1,3}',
	'public_law_section': '[ ]{1,7}(\S+[ ]\"\S+[ ][\S\'\"]+)|[ ]{1,7}(\S+[ ]\S*)|([ ])', 
	#public_law_section regex notes: The first option is in case of quotes, the second option is the norm, and the last option is in case it is empty.
	'statutes_at_large_section': '[ ]+\d*A?[,-]?[ ]?\d*',
	'statutes_at_large_volume': '\d{1,3}',    
	'description': '(nt[\[\]a-zA-Z ]*)|(ed chg)|(prec[a-zA-Z ]*)|(new)|(gen amd)|(omitted)|(repealed)|(tr to [\w/-]*)|(tr fr [\w/-]*)|(to [:\w/-]*)|(fr [\w/-]*)|([\[\]\.a-zA-Z -]+)',
}
	
LINE_TYPES = {
	'normal_line': re.compile(r"{usc_title}[ ]*{usc_section}[ ]*({description})?[ ]*{public_law_number}[ ]({public_law_section})[ ]*{statutes_at_large_section}[ ]+{statutes_at_large_volume}".format(**EXPRESSIONS)),
	'additional_description_line': re.compile(r"^[ ]{5,1000}.+$"),
}


def classify(line):
    return dict([
        (type, expr.match(line))
    for type, expr in LINE_TYPES.items()])


lines1 = re.compile(r'\n').split(full_content1)  

lines1.pop(0) #Remove superfluous first line of text.
statutes_volume_line1 = lines1.pop(0) #Capture and remove second line of text (which contains Statutes at Large Volume)
lines1.pop(0) #Remove superfluous third line of text.

a = re.search("(\d+)", statutes_volume_line1) 
statutes_volume1 = a.group() #Saves Statutes at Large Volume for the first year of this congressional session.
lines1 = [y + "     " + statutes_volume1 for y in lines1] #Adds Statutes at Large Volume to end of each string.

lines2 = re.compile(r'\n').split(full_content2)

lines2.pop(0) #Remove superfluous first line of text.
statutes_volume_line2 = lines2.pop(0) #Capture and remove second line of text (which contains Statutes at Large Volume)
lines2.pop(0) #Remove superfluous third line of text.

b = re.search("(\d+)", statutes_volume_line2)
statutes_volume2 = b.group() #Saves Statutes at Large Volume for the second year of this congressional session.
lines2 = [x + "     " + statutes_volume2 for x in lines2] #Adds Statutes at Large Volume to end of each string.

lines = lines1 + lines2 #Combine first and second years of congressional session.

lines_length = len(lines)



usc_title = None
usc_section = None
public_law_number = None
public_law_section = None
statutes_at_large_section = None
counter = 0
additional_counter = 0

line_data = {}	
listout = []	

for line in lines:
			
	classified = classify(line)
		
	if classified['normal_line']:

		f = re.match(r"(?P<usc_title>{usc_title})[ ]*(?P<usc_section>{usc_section})[ ]+(?P<description>{description})[ ]*(?P<public_law_number>{public_law_number})[ ](?P<public_law_section>{public_law_section})[ ]*(?P<statutes_at_large_section>{statutes_at_large_section})[ ]+(?P<statutes_at_large_volume>{statutes_at_large_volume})".format(**EXPRESSIONS), line)

		line_data = f.groupdict()

		line_data = {k: v.strip() for k, v in line_data.iteritems()} #removes whitespace
			
		if ',' in line_data['statutes_at_large_section']:
			line_data['statutes_at_large_section'] = re.split(',', line_data['statutes_at_large_section'])

		if '-' in line_data['statutes_at_large_section']:
			statutes_ends = []
			statutes_ends = re.split('-', line_data['statutes_at_large_section'])
				
			statutes_high = int(statutes_ends.pop())
			statutes_low = int(statutes_ends.pop())

			line_data['statutes_at_large_section'] = range(statutes_low, statutes_high + 1)

		if ',' in line_data['public_law_section']: 
			line_data['public_law_section'] = re.split(',', line_data['public_law_section'])



		counter = counter + 1
		listout.append(line_data)
		
	elif classified['additional_description_line']:
			
		f = re.match("(?P<additional_description>.*$)", line)
			
		line_data = f.groupdict()
		line_data = {k: v.strip() for k, v in line_data.iteritems()} #removes whitespace		
		#print line_data

		#previous_line = listout.pop()
		#print previous_line

		#line_data = previous_line + line_data
		#listout.append(line_data)

		additional_counter = additional_counter + 1
       
	else:
		print "This is a problem line...", line


jsonfile = json.dumps(listout, indent=5)
print jsonfile

print "There were %s items in this list." %lines_length 
print "There are %s items accounted for in the output." %counter
print "There are %s additional description lines unaccounted for in this output." %additional_counter




#TO DO:
#create separate rows for multiple inset usc_section listings
#add additional descriptions to previous dict
#ffix the (very small number of) lines that aren't getting picked up
