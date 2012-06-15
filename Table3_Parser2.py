#Table 3 Parser
#United States Code: Table of Classifications for Public Laws
#Alex Engler
#Sunlight Foundation


import re
from collections import OrderedDict
import csv
import copy

EXPRESSIONS = {
	'usc_title': '^\d\d?A?',
	'usc_section': '[ ]\d{1,5}\w*-?\w*',
	'public_law_number': '\d{1,3}-\d{1,3}',
	'public_law_section': '([\d()]{1,5}[()\w,-]*[ ][()\w"]*)|([ ])',
	'statutes_at_large': '\s\d*[,-]?[ ]?\d*$',    
	'description': '(nt[\[\]a-zA-Z ]*)|(ed chg)|(prec[a-zA-Z ]*)|(new)|(gen amd)|(omitted)|(repealed)|(tr to [\w/-]*)|(tr fr [\w/-]*)|([a-zA-Z -]+)',
}
	
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
	
	usc_title = None
	usc_section = None
	public_law_number = None
	public_law_section = None
	statutes_at_large = None
	
	line_data = {}		

	for line in lines:
		if not line.strip():
			continue
			
		classified = classify(line)
		previous_line_data = copy.deepcopy(line_data)
		
		if classified['normal_line']:
			
			f = re.match("(?P<usc_title>{usc_title})[ ]+(?P<usc_section>{usc_section})[ ]+(?P<description>{description})[ ]+(?P<public_law_number>{public_law_number})[ ]+(?P<public_law_section>{public_law_section})[ ]+(?P<statutes_at_large>{statutes_at_large})".format(**EXPRESSIONS), line)

			line_data = f.groupdict()
			line_data = {k :v.strip() for k, v in line_data.iteritems()} #removes whitespace			
		
			writer.writerow(line_data)
			
			print line_data
		
		if classified['additional_description_line']:
			
			f = re.match("(?P<additional_description>.*$)", line)
			
			line_data = f.groupdict()
			line_data = {k :v.strip() for k, v in line_data.iteritems()} #removes whitespace		
						
			print line_data
       
		if not any(classified):
			print 'What kind of line is this?', line
			sys.exit(1)


file_target = raw_input("Enter Table 3 file to be parsed: ")
file = open(file_target)	

output_file = open('table3.csv', 'w')

writer= csv.DictWriter(output_file, ['usc_title', 'usc_section', 'public_law_number', 'public_law_section', 'statutes_at_large', 'description'])
writer.writeheader()

parse_table3(file)

output_file.close()


#TO DO:
#create separate rows for multiple usc_section listings
#add additional descriptions to previous dict
#name of csv
#scrapper compliance
#statues being picked up as public law sections when there is no public law section
