    # -*- coding: utf-8 -*-
import os
import xlrd
import logging
import pandas as pd

import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from bs4 import BeautifulSoup
from bs4.element import Comment

from wikicrawler.items import WikicrawlerItem

# Logger instance
logging.basicConfig(filename='crawl.log')
logger = logging.getLogger(__name__)

class WikipediaSpider(scrapy.Spider):
    name = 'wikispider'

    # Helper variables
    link_counter = 1
    visited_urls = list()

    # Initializing to visit links. Hardcode
    abs_path = os.path.dirname(__file__) + '/../../'
    df = pd.read_excel(abs_path + 'web_links.xlsx') 

    # Filter to ensure only wikipedia pages are crawled
    visit_urls = [x for x in df['Url'].dropna().tolist() 
    				if 'https://en.wikipedia.org' in x]

    def start_requests(self):
    	'''
    	Initiates crawling
    	'''
    	for url in list(self.visit_urls):
    		# Iterating over copy of urls so as to modify urls

			# Popping visited urls
    		self.visit_urls.remove(url)

    		# Crawling unvisited pages
    		if url not in self.visited_urls:
    			yield scrapy.Request(url, callback=self.parse_first_page)

    def parse_first_page(self, response):
    	'''
    	Function receives crawled page
    	'''
    	# Logging
    	logger.debug('Crawling 1st page link{0} : {1}'.format(self.link_counter, 
    															response.url))
    	# Storing data
    	item = self.store_data(response)  

    	# Parsing response for link extraction
    	soup = BeautifulSoup(response.body, features="lxml")  		

    	# Setting up crawling of second page i.e. child links
    	ext_links = WikipediaSpider.get_see_also(soup, response.url)
    	for url in ext_links:
    		if url not in self.visited_urls:
    			yield scrapy.Request(url, callback=self.parse_second_page)   	

    	return item

    def parse_second_page(self, response):
        '''
        Function receives crawled page
        '''
        # Logging
        logger.debug('Crawling 2nd page link{0} : {1}'.format(self.link_counter, 
                                                                response.url))
        # Storing data
        item = self.store_data(response)

        # Parsing response for link extraction
        soup = BeautifulSoup(response.body, features="lxml")

        # Setting up crawling of second page i.e. child links
        ext_links = WikipediaSpider.get_see_also(soup, response.url)
        for url in ext_links:
            if url not in self.visited_urls:
                yield scrapy.Request(url, callback=self.parse_third_page)

        return item

    def parse_third_page(self, response):
        '''
        Function receives crawled page
        '''
        # Logging
        logger.debug('Crawling 3rd page link{0} : {1}'.format(self.link_counter, 
                                                                response.url))
        # Storing data
        item = self.store_data(response)

        return item

    def store_data(self, response):
    	'''
    	Prepares item from response body
    	'''
   		# Incrementing link counter
    	self.link_counter += 1

        # Prevent re-crawling of links
    	self.visited_urls.append(response.url)

    	# Parsing response
    	soup = BeautifulSoup(response.body, features="lxml")

    	# Filling item
    	item = WikicrawlerItem()
    	item['link'] = response.url

    	# Getting only visible text from webpage
    	texts = soup.findAll(text=True)
    	visible_texts = filter(WikipediaSpider.tag_visible, texts)  
    	item['text'] = " ".join(t.strip() for t in visible_texts) 

    	return item
    	
    def get_see_also(soup, parent_url):
    	'''
    	Custom function to return see also wiki links from wiki pages
    	'''
    	links = list()
    	req_heading = ''

    	# Finding See also in wiki page
    	headings = soup.find_all("h2")
    	for heading in headings:
    		if heading.find("span",id='See_also'):
    			req_heading = heading
    			break

    	if req_heading:
    		# See also was found in wiki page
    		# Getting set of ul having links
    		node = req_heading.find_next('ul').find_next('ul')
    		for li in node.find_all('li'):
    			a = li.find('a')
    			if a and 'wiki' in a['href']:
    				links.append(parent_url.split('/wiki')[0] + a['href'])
 
    	return links

    def tag_visible(element):
    	'''
    	Getting data from wiki page
    	'''
    	if element.parent.name in ['style', 'script', 'head', 'title', 'meta', 
                                    '[document]']:
    		return False
    	if isinstance(element, Comment):
    		return False

    	return True
