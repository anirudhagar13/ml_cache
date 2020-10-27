# ml_cache
Optimising cache admission using Machine Learning

# Hierarchy of project:
- mlcache: Django project
	- mlcache: central application

# Dev Env setup:
- `sh dev_setup.sh`

# Web crawler operations:
- [Reference API for crawler code](https://docs.scrapy.org/en/latest/intro/tutorial.html)
- By defaut goes to 3 level of scraping i.e. does not picks up pages from 3rd child page in BFS mannner
- execute command from `mlcache` directory
- command: `scrapy crawl 'botname' -o 'output file path'`
	- eg: (scrapy crawl wikispider -o static/mlcache/wiki_pages.json)
- *Note:* Put some effort in making functions recursive, but didn't work out.