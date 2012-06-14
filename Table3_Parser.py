#Table 3 Parser
#United States Code: Table of Classifications for Public Laws
#Alex Engler
#Sunlight Foundation


import sys
import re
from collections import OrderedDict


EXPRESSIONS = {
	'usc_title': '^\d\d?A*',	#use multiline mode
	'usc_section': '[ ]\d{1,5}\w*-?\w*',
	'public_law_number': '\d{1,3}-\d{1,3}', #may match some public law section numbers
	'public_law_section': '[ ] [\d()]{1,5}[()\w,-]*[ ][()\w"]*',
	'statutes_at_large': '\s\d*[,-]?[ ]?\d*$',
	'description': '(nt[\[\]a-zA-Z ]*)|(ed chg)|(prec[a-zA-Z ]*)|(new)|(gen amd)|(omitted)|(repealed)|(tr to [\w/-]*)|(tr fr [\w/-]*)|([a-zA-Z -]+)',
}

#account for any weird descriptions
#account for lines with no public law section

	
LINE_TYPES = {
	'normal_line': re.compile(r"{usc_title} [ ]* {usc_section}[ ]* ({description})?[ ]* {public_law_number}[ ]* ({public_law_section})?[ ]* {statutes_at_large}$".format(**EXPRESSIONS)),
	'additional_description_line': re.compile(r"^[ ]{5,1000}.+$"),
}

##AS GOOD AS IT'S GETTING: normal_line complete
##^\d\d?A* [ ]* [ ]\d{1,5}\w*-?\w*[ ]+((nt[\[\]a-zA-Z ]*)|(ed chg)|(prec[a-zA-Z ]*)|(new)|(gen amd)|(omitted)|(repealed)|(tr to [\w/-]*)|(tr fr [\w/-]*)|([a-zA-Z -]+))[ ]+\d{1,3}-\d{1,3} [ ]+([\d()]{1,5}[()\w,-]*[ ][()\w"]*)? [ ]+ \s\d*[,-]?[ ]?\d*$


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
			line_data = classified['normal_line'].groupdict()
			current_usc_title = line_data['usc_title']
			
			#current_usc_section = line_data['usc_section']
			#current_public_law_number = line_data['usc_section']
			#current_public_law_section = line_data['usc_section']
			#current_statutes_at_large = line_data['usc_section']
			
			#parsed[current_usc_title][current_usc_section][current_public_law_number][current_public_law_section][current_statutes_at_large] = OrderedDict()
			
			return parsed
			print parsed
			
			
     	if line == "    ":
            print 'Done!'
            return parsed
        
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
import csv

