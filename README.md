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
	: 'token' - name of models to be saved across pipeline, with set configurations and dataset
	: 'tpath' - path of training data file
- To train and save model, after figuring out best hyperparameters
	: `python -m document_classifier.main --token bbc --tpath 'document_classifier/data/BBC News Train.csv' --save True`
	: 'save' - train on complete data with set configurations and save model, by default does 5-fold cross validation
- To predict document classes using trained and saved model
	: `python -m document_classifier.main --token bbc --ppath 'document_classifier/data/BBC News Test.csv' > document_classifier/data/predictions.txt`
	: 'ppath' - Path of data on which predictions to be made

# Wikipedia data Document classification:
- [Dataset Link](http://www.zubiaga.org/datasets/wiki10+/)
- Download and store dataset in the `data` folder within document_classifier. Also unzip it.
- To prepare data, run command 
	: `python -m document_classifier.wiki_data_prep --tag tag-data.xml --data documents --ofile wiki_data.csv`
	: 'tag' - file name with metadata and tags 
	: 'data' - should be directory name containing all wikipedia pages,
	: 'ofile' - output csv filename to store wikipedia dataset after processing
- After data is prepared, can follow above Document classifier commands, with updated data path, to tune classifier i.e.
	: `python -m document_classifier.main --token wiki --tpath 'document_classifier/data/wiki_data.csv'`

# Run code to connect crawler and classifier:
- Download trace file from this [link](http://www.wikibench.eu/?page_id=60)
- Unzip and place trace file inside web_crawler folder
- Change file name and run `python trace_preprocess.py`
- Run webcrawler using above command
- Run command `python crawled_preprocess.py`