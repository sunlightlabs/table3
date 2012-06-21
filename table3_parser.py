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

html_parser = etree.HTMLParser()

URLS = {
	1 : "http://uscodebeta.house.gov/classification/tbl%spl_1st.htm",
	2 : "http://uscodebeta.house.gov/classification/tbl%spl_2nd.htm"
}

URLS_104 = {
	1 : "http://uscodebeta.house.gov/classification/tbl%spl.htm"
}		


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
	'normal_line': re.compile(r"{usc_title}[ ]*{usc_section}[ ]*({description})?[ ]*{public_law_number}[ ]({public_law_section})[ ]*{statutes_at_large_section}[ ]+{statutes_at_large_volume}".format(**EXPRESSIONS))
}


usc_title = None
usc_section = None
public_law_number = None
public_law_section = None
statutes_at_large_section = None

line_data = {}
listout = []

HARD_CODED_LINES = json.load(open("hard_coded_lines.json"))


def classify(line):
    return dict([
        (type, expr.match(line))
    for type, expr in LINE_TYPES.items()])


def parse_line(line):
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

		return line_data
       
	elif line in HARD_CODED_LINES:
			return HARD_CODED_LINES[line]

	else:
		print "This is a problem line...", line


if __name__ == "__main__":
	congress_session = argv[1]
	lines = []

	urls = URLS_104 if congress_session == '104' else URLS

	for page in sorted(urls.keys()):
		connection = urllib2.urlopen(urls[page] % congress_session)
		page_content = connection.read()
		page = etree.parse(StringIO.StringIO(page_content), html_parser)

		if congress_session == '104':
			tag_content = CSSSelector('.page_content_internal pre')(page)[0]
			full_content = tag_content.text.strip()
			page_lines = re.compile(r'\n').split(full_content)

			del page_lines[:51] #removes extra text within the <pre> tab that is unique to the 104th congress

			page_lines.pop(0)
			page_lines.pop(0)
			page_lines.pop(0)

			page_lines = [y + "     111" for y in page_lines] #half are 111, half are 112, fix that somehow?

		else: 

			if congress_session == '105':
				tag_content = CSSSelector('.page_content_internal pre')(page)[0]
				full_content = tag_content.text.strip()
				page_lines = re.compile(r'\n').split(full_content)
			
				del page_lines[:50] #removes extra text within the <pre> tab that is unique to the 105th congress
				if page_lines.count('') == 1:
					page_lines.remove('') #removes single extra whitespace line that is unique to first year of 105th congress page

			else:
				tag_content = CSSSelector('.page_content_internal pre font')(page)[0]
				full_content = tag_content.text.strip()
				page_lines = re.compile(r'\n').split(full_content)  

		print page_lines

		page_lines.pop(0) #Remove superfluous first line of text.
		statutes_volume_line = page_lines.pop(0) #Capture and remove second line of text (which contains Statutes at Large Volume)
		page_lines.pop(0) #Remove superfluous third line of text.

		a = re.search("(\d+)", statutes_volume_line) 
		statutes_volume = a.group() #Saves Statutes at Large Volume for the first year of this congressional session.
		page_lines = [y + "     " + statutes_volume for y in page_lines] #Adds Statutes at Large Volume to end of each string.

		lines += page_lines
	lines_length = len(lines)



	for line in lines:
		parsed_line = parse_line(line)
		if parsed_line:
			listout.append(parse_line(line))


	jsonfile = json.dumps(listout, indent=5)
	print jsonfile

	print "There were %s items in this list." %lines_length 
	print "There are %s items accounted for in the output." % len(listout)




#TO DO:
#create separate rows for multiple inset usc_section listings
#add additional descriptions to previous dict
#fix the (very small number of) lines that aren't getting picked up
