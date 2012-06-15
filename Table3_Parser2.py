#Table 3 Parser
#United States Code: Table of Classifications for Public Laws
#Alex Engler
#Sunlight Foundation


import sys
import re
from collections import OrderedDict
import csv

EXPRESSIONS = {
	'usc_title': '^\d\d?A?',
	'usc_section': '[ ]\d{1,5}\w*-?\w*',
	'public_law_number': '\d{1,3}-\d{1,3}',
	'public_law_section': '([\d()]{1,5}[()\w,-]*[ ][()\w"]*)|([ ])',
	'statutes_at_large': '\s\d*[,-]?[ ]?\d*$',    
	'description': '(nt[\[\]a-zA-Z ]*)|(ed chg)|(prec[a-zA-Z ]*)|(new)|(gen amd)|(omitted)|(repealed)|(tr to [\w/-]*)|(tr fr [\w/-]*)|([a-zA-Z -]+)',
}

#account for any weird descriptions

#account for additional sections that should be separate entries
	
LINE_TYPES = {
	'normal_line': re.compile(r"{usc_title} [ ]* {usc_section}[ ]* ({description})?[ ]* {public_law_number}[ ]* ({public_law_section})?[ ]* {statutes_at_large}$".format(**EXPRESSIONS)),
	'additional_description_line': re.compile(r"^[ ]{5,1000}.+$"),
}


def classify(line):
    return dict([
        (type, expr.match(line))
    for type, expr in LINE_TYPES.items()])

def parse_table3(file):	
	full_content = file.read()
	lines = re.compile(r'\n').split(full_content)  
	del full_content
	
	current_usc_title = None
	current_usc_section = None
	current_public_law_number = None
	current_public_law_section = None
	current_statutes_at_large = None
	parsed = OrderedDict()
	
	for line in lines:
		if not line.strip():
			continue

		classified = classify(line)
		line_data = None
		
		if classified['normal_line']:
			
			f = re.match("(?P<current_usc_title>{usc_title})[ ]+(?P<current_usc_section>{usc_section})[ ]+(?P<current_description>{description})[ ]+(?P<current_public_law_number>{public_law_number})[ ]+(?P<current_public_law_section>{public_law_section})[ ]+(?P<current_statutes_at_large>{statutes_at_large})".format(**EXPRESSIONS), line)

			line_data = f.groupdict()

			current_usc_title = line_data['current_usc_title']
			current_usc_section = line_data['current_usc_section']
			current_description = line_data['current_description']
			current_public_law_number = line_data['current_public_law_number']
			current_public_law_section = line_data['current_public_law_section']
			current_statutes_at_large = line_data['current_statutes_at_large']
			
			##something like  writer = csv.writer(open('table.csv', 'wb')?
			
			print line_data
		
		if classified['additional_description_line']:
			
			f = re.match("(?P<additional_description>.*$)", line)
			
			line_data = f.groupdict()
		
			current_additional_description = line_data['additional_description']
			
			print line_data			
		
       
		if not any(classified):
			print 'Something went wrong...', line
			print parsed
			sys.exit(1)



#Open file
file_target = raw_input("Enter Table 3 file to be parsed: ")
file = open(file_target)	
#/Users/AlexEngler/Desktop/Python Docs/Table3_112.txt
	
parse_table3(file)

#export to .csv


