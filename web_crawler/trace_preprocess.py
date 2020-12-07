# Preprocesses wiki trace data @ http://www.wikibench.eu/?page_id=60
# Makes trace compatible to the web crawler
import pandas as pd

url_list = list()
timestamp_list = list()
with open('wiki.1190153705', encoding = "ISO-8859-1") as infile:
    for line in infile:
        
        url = line.split()[2]
        timestamp = line.split()[1]
        if 'http://en.wikipedia.org/wiki/' in url:
            url_list.append(url)
            timestamp_list.append(timestamp)

pd.DataFrame(data={'Url': url_list, 'time': timestamp_list}).to_csv('web_links.csv')
