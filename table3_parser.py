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
	'public_law_section': '[ ]{1,7}(.+[\]])|([ ]{1,7}(\S+[ ]\"\S+[ ][\S\'\"]+))|([ ]{1,7}(\S+[ ]\S*))|([ ])', 
	#public_law_section regex notes: The first option is in case of quotes, the second option is the norm, and the last option is in case it is empty.
	'statutes_at_large_page': '([ ]*\d*A?[,-]?[ ]?\d*((,?[ ]?)|( to ))\d*A?[-]?\d+)',
	'statutes_at_large_volume': '\d{1,3}',    
	'description': '(nt[\[\]a-zA-Z ]*)|(R Plan \d, \d{4})|(ed chg)|(prec[a-zA-Z ]*)|(new)|(gen amd)|(omitted)|(repealed)|(tr to [\w/-]*)|(tr fr [\w/-]*)|(to [:\w/-]*)|(fr [\w/-]*)|([\[\]\.a-zA-Z -]+)',
}
	
LINE_TYPES = {
	'normal_line': re.compile(r"{usc_title}[ ]*{usc_section}[ ]*({description})?[ ]*{public_law_number}[ ]({public_law_section})[ ]?{statutes_at_large_page}[ ]+{statutes_at_large_volume}".format(**EXPRESSIONS))
}


usc_title = None
usc_section = None
public_law_number = None
public_law_section = None
statutes_at_large_page = None

line_data = {}
ignored_lines = {}	
listout = []

HARD_CODED_LINES = json.load(open("hard_coded_lines.json"))


def classify(line):
    return dict([
        (type, expr.match(line))
    for type, expr in LINE_TYPES.items()])


def splitter(line_data):
 	##alter statutes_at_large_page into one of three types of arrays
 	print line_data
 	if line_data['statutes_at_large_page'] == "":
 		print line
 		print "Issue Statute!!!"

 	if ',' in line_data['statutes_at_large_page'] and 'A-' in line_data['statutes_at_large_page']:
 		line_data['statutes_at_large_page'] = re.split(',', line_data['statutes_at_large_page'])
 		#next three lines just remove whitespace created by split
 		first_statute_section = line_data['statutes_at_large_page'].pop(0).strip()
 		second_statute_section = line_data['statutes_at_large_page'].pop(0).strip()
 		line_data['statutes_at_large_page'] = [first_statute_section, second_statute_section]

 	elif 'to' in line_data['statutes_at_large_page'] and 'A-' in line_data['statutes_at_large_page']:
 		line_data['statutes_at_large_page'] = re.split('to', line_data['statutes_at_large_page'])
 		#next three lines just remove whitespace created by split
 		statute_low = line_data['statutes_at_large_page'].pop(0).strip()
 		statute_high = line_data['statutes_at_large_page'].pop(0).strip()
 		line_data['statutes_at_large_page'] = [{"start": statute_low, "end": statute_high}]

 	elif 'to' in line_data['statutes_at_large_page']: # e.g. 2681-326 to 2681-335
 		statutes_ends = re.split('to', line_data['statutes_at_large_page'])
		statute_low = statutes_ends.pop(0).strip()
 		statute_high = statutes_ends.pop(0) .strip()
 		line_data['statutes_at_large_page'] = [{"start": statute_low, "end": statute_high}]

 	elif ','  in line_data['statutes_at_large_page'] and '-' in line_data['statutes_at_large_page']:
 		pass
 		#do something, if this is a real problem....
 		#
 		#
 		#notice this.....


 	elif ',' in line_data['statutes_at_large_page']:
 		line_data['statutes_at_large_page'] = re.split(',', line_data['statutes_at_large_page'])
 		#next three lines just remove whitespace created by split
 		first_statute_section = line_data['statutes_at_large_page'].pop(0).strip()
 		second_statute_section = line_data['statutes_at_large_page'].pop(0).strip()
 		line_data['statutes_at_large_page'] = [first_statute_section, second_statute_section]

	elif 'A-' in line_data['statutes_at_large_page']:
		line_data['statutes_at_large_page'] = [line_data['statutes_at_large_page']]

	elif '-' in line_data['statutes_at_large_page']: 

		if re.match(r"\d{4}[-]\d{4}", line_data['statutes_at_large_page']) is not None:
 			statutes_ends = re.split('-', line_data['statutes_at_large_page'])
 			statute_low = statutes_ends.pop(0)
 			statute_high = statutes_ends.pop(0) 
 			line_data['statutes_at_large_page'] = [{"start": statute_low, "end": statute_high}]

		elif re.match(r"\d{4}[-]\d{1,3}", line_data['statutes_at_large_page']) is not None:
			#so as to not catch statutes at large sections with subsections denoted by hyphens e.g. 1621-758
			line_data['statutes_at_large_page'] = [line_data['statutes_at_large_page']]

		else:
 			statutes_ends = re.split('-', line_data['statutes_at_large_page'])
 			statute_low = statutes_ends.pop(0)
 			statute_high = statutes_ends.pop(0) 
 			line_data['statutes_at_large_page'] = [{"start": statute_low, "end": statute_high}]
 		
 	else:
 		line_data['statutes_at_large_page'] = [line_data['statutes_at_large_page']]
 	
 	
	#alters public law sections into one of three types of arrays
 	if ',' in line_data['public_law_section'] and '-' in line_data['public_law_section']:
 		pass
 		print "Both  ", line_data['public_law_section']

 	elif ',' in line_data['public_law_section'] and '[' in line_data['public_law_section']:
 		pass

 	elif ','in line_data['public_law_section']:
 		plsections = re.split(',', line_data['public_law_section'])
		plsection_low = plsections.pop(0).strip()
 		plsection_high = plsections.pop(0).strip()


		if re.match(r"\d+\([a-z]\)\(\d+\)\([A-Z]\)\([ivx]+\)", plsection_low) is not None and re.match(r"\([ixv]", plsection_high): 
			plsection_base = re.match(r"\d+\([a-z]\)\(\d+\)\([A-Z]\)", plsection_low).group()
			line_data['public_law_section'] = [plsection_low, plsection_base + plsection_high]

		elif re.match(r"\d+", plsection_low) is not None and re.match(r"\d+", plsection_high) is not None:
			line_data['public_law_section'] = [plsection_low, plsection_high]

		elif re.match(r"\d+\w?\([a-z]{1,2}\)\(?\w*", plsection_low) is not None and re.match(r"\([a-z]{1,2}\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+\w?", plsection_low).group()
			line_data['public_law_section'] = [plsection_low, plsection_base + plsection_high]

		elif re.match(r"\d+\([a-z]{1,2}\)\(\d+\)", plsection_low) is not None and re.match(r"\(\d+\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+\([a-z]{1,2}\)", plsection_low).group()
			line_data['public_law_section'] = [plsection_low, plsection_base + plsection_high]

		elif re.match(r"\d+\([a-z]\)\(\d+\)\([A-Z]+\)", plsection_low) is not None and re.match(r"\([A-Z]+\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+\([a-z]\)\(\d+\)", plsection_low).group()
			line_data['public_law_section'] = [plsection_low, plsection_base + plsection_high]

		elif re.match(r"\d+\(\d+\)", plsection_low) is not None and re.match(r"\(\d+\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+", plsection_low).group()
			line_data['public_law_section'] = [plsection_low, plsection_base + plsection_high]

		else:	
			print "Comma problem!!!!----------------"

	elif '-' in line_data['public_law_section']:
		plsection_ends = re.split('-', line_data['public_law_section'])
		plsection_low = plsection_ends.pop(0).strip()
		plsection_high = plsection_ends.pop(0).strip()
		print plsection_low
		print plsection_high

		if re.match(r"\d+", plsection_low) is not None and re.match(r"\d+.?", plsection_high) is not None:
			line_data['public_law_section'] = [{"start": plsection_low, "end": plsection_high}]
			print "We got this one, right?"
			print line_data

		elif re.match(r"\d+A?\([a-z]\)", plsection_low) is not None and re.match(r"\([a-z]\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+", plsection_low).group()
			line_data['public_law_section'] = [{"start": plsection_low, "end": plsection_base + plsection_high}]
			print "We got this one, right?"
			print line_data
			

		elif re.match(r"\d+\([a-z]\)\(\d+\)", plsection_low) is not None and re.match(r"\(\d+\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+\([a-z]\)", plsection_low).group()
			line_data['public_law_section'] = [{"start": plsection_low, "end": plsection_base + plsection_high}]
			print "We got this one, right?"
			print line_data
			
		elif re.match(r"\d+\([a-z]\)\(\d+\)\([A-Z]{1,2}\)", plsection_low) is not None and re.match(r"\([A-Z]{1,2}\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+\([a-z]\)\(\d+\)", plsection_low).group()
			line_data['public_law_section'] = [{"start": plsection_low, "end": plsection_base + plsection_high}]
			print "We got this one, right?"
			print line_data

		elif re.match(r"\d+\(\d+\)", plsection_low) is not None and re.match(r"\(\d+\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+", plsection_low).group()
			line_data['public_law_section'] = [{"start": plsection_low, "end": plsection_base + plsection_high}]
			print "We got this one, right?"
			print line_data	

		elif re.match(r"\d+\([a-z]\)\(\d+\)\([A-Z]\)\([ivx]+\)", plsection_low) is not None and re.match(r"\([ivx]+\)", plsection_high) is not None:
			plsection_base = re.match(r"\d+\([a-z]\)\(\d+\)\([A-Z]\)", plsection_low).group()
			line_data['public_law_section'] = [{"start": plsection_low, "end": plsection_base + plsection_high}]
			print "We got this one, right?"
			print line_data	

		else:
			line_data['public_law_section'] = [{"start": plsection_low, "end": plsection_high}]
			print "Hyphen!!!!!--------------"
			#There are more cases to be accounted for.....
			pass


 	else:
 		line_data['public_law_section'] = [line_data['public_law_section']]
 		
 	return line_data


def parse_line(line):

	classified = classify(line)
	if line in HARD_CODED_LINES:
		return HARD_CODED_LINES[line]
		
	elif classified['normal_line']:
		f = re.match(r"(?P<usc_title>{usc_title})[ ]*(?P<usc_section>{usc_section})[ ]+(?P<description>{description})[ ]*(?P<public_law_number>{public_law_number})[ ](?P<public_law_section>{public_law_section})[ ]*(?P<statutes_at_large_page>{statutes_at_large_page})[ ]+(?P<statutes_at_large_volume>{statutes_at_large_volume})".format(**EXPRESSIONS), line)

		line_data = f.groupdict()
		line_data = {k: v.strip() for k, v in line_data.iteritems()} #removes whitespace

		line_data = splitter(line_data)

		return line_data

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

			del page_lines[:54] #removes extra text within the <pre> tab that is unique to the 104th congress

			while page_lines.count('') > 0:
				page_lines.remove('') #removes empty lines specific to the 104th congress
			page_lines = [y + "     109" for y in page_lines[:1511]] + [y + "     110" for y in page_lines[1511:]] #correctly attributes statutes volume to 104th congress

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
			listout.append(parsed_line)


	jsonfile = json.dumps(listout, indent=5)
	print "There were %s items in this list." %lines_length 
	print "There are %s items accounted for in the output." % len(listout)



