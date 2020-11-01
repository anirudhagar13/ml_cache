# Prepares Wikipedia data for document classification pipeline
# http://www.zubiaga.org/datasets/wiki10+/

import os
import argparse
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as BS

# Present working directory
data_path = os.path.dirname(os.path.realpath(__file__)) + '/data/'

# Targets planned to extract
wiki_targets = ['art','culture','books','design','politics','technology',
			'psychology','religion','music','math','development','theory',
			'philosophy','language','science','history','software']

def extract_tags(xml_file_path):
	'''
	Creates a map of document and target tag found among the targets
	If a tag for a document not found in targets, that document is ignored
	'''
	hash_list = list()
	tag_list = list()

	tree = ET.parse(xml_file_path)
	root = tree.getroot()
	articles = root.findall('article')

	# looping through all articles
	for idx, article_ in enumerate(articles):
		tags = article_.findall('tags')

		for tag_ in tags:
			tag_name = tag_.find('tag').find('name').text.lower()

			if tag_name in wiki_targets:
				# Adding only documents for which target found
				tag_list.append(tag_name)
				hash_list.append(article_.find('hash').text)
				break

	return hash_list, tag_list

def parse_html(wiki_data_path, hash_list):
	'''
	Reads html of pages from path and parses text
	'''
	doc_list = list()
	for idx, hash_ in enumerate(hash_list):
		document = list()

		with open(data_path + args.data + '/' + hash_, 'r') as fp: 
			document = fp.read() 

		soup = BS(document, features="html.parser")

		# kill all script and style elements
		for script in soup(["script", "style"]):
			script.extract()    # rip it out

		# get text
		text = soup.get_text()

		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in text.splitlines())

		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

		# drop blank lines
		text = ' '.join(chunk for chunk in chunks if chunk)

		doc_list.append(text)

		if idx % 400 == 0:
			print ('Completed parsing HTML Documents: ', idx)

	return doc_list

if __name__ == '__main__':
	# Define the parser, to read the input arguments
	parser = argparse.ArgumentParser(description='Wiki dataset extraction')

	# Absolute path of training file and prediction file
	parser.add_argument('--tag', action="store", dest='tag', default='')
	parser.add_argument('--data', action="store", dest='data', default='')
	parser.add_argument('--ofile', action="store", dest='ofile', default='wiki_data.csv')

	args = parser.parse_args()

	if args.tag == '' or args.data == '':
		print ('Input arguments, tag-file name and data directory not provided.')
		sys.exit()

	hash_list, tag_list = extract_tags(data_path + args.tag)
	doc_list = parse_html(data_path + args.data, hash_list)

	# Saving data in csv files
	df = pd.DataFrame({'documents': doc_list, 'categories': tag_list})
	df.to_csv(data_path + args.ofile, index=False)
	