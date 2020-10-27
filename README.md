# ml_cache
Optimising cache admission using Machine Learning

# Dev Env setup:
- `sh dev_setup.sh`

# Web crawler operations:
- [Reference API for crawler code](https://docs.scrapy.org/en/latest/intro/tutorial.html)
- By defaut goes to 3 level of scraping i.e. does not picks up pages from 3rd child page in BFS manner
- Execute command from `web_crawler` directory
- command: `scrapy crawl 'botname' -o 'output file path'`
	- eg: (scrapy crawl wikispider -o wiki_pages.json)
- *Note:* Did put some effort in making functions recursive, but didn't work out.

# Document classifier operations:
- Download sample data from [Kaggle BBC](https://www.kaggle.com/c/learn-ai-bbc/data)
- Save data (Train and Test) in `document_classifier/data` folder
- Run the below commands from `ml_cache` directory
- To train and tune by validating using cross-validation accuracy scores
	: `python -m document_classifier.main --token bbc --tpath 'document_classifier/data/BBC News Train.csv'`
- To train and save model, after figuring out best hyperparameters
	: `python -m document_classifier.main --token bbc --tpath 'document_classifier/data/BBC News Train.csv' --save True`
- To predict document classes using trained and saved model
	: `python -m document_classifier.main --token bbc --ppath 'document_classifier/data/BBC News Test.csv' > document_classifier/data/predictions.txt`