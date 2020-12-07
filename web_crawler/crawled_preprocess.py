# Converts output of web crawler for document classifier
import json 
import pandas as pd

data = dict()
with open('wiki_pages.json') as json_file: 
	data = json.load(json_file)

text_list = list()
link_list = list()
for row in data:
	text_list.append(row['text'])
	link_list.append(row['link'])

pd.DataFrame(data={'Text': text_list, 'link': link_list}).to_csv('to_predict.csv', index=False)
