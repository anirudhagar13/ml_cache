'''
Client interface for running control flow in document classification
'''
import os
import sys
import argparse
import operator
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from .files import read_from_csv
from .encoder import encoderFactory
from .evaluate import validateFactory
from .estimator import estimatorFactory
from .language_processing import preprocessing
from .transformer import vectorizerFactory, dimensionFactory

# logging
import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def data_evenness(data):
	'''
	converts data to standard and even format by renaming columns
	'''
	if isinstance(data, dict):
		data = pd.DataFrame.from_dict(data)

	# Renaming following columns
	doc_col_names = ['Text']
	cat_col_names = ['Category']
	doc_ren_name = [x for x in doc_col_names if x in data.columns.values]
	cat_ren_name = [x for x in cat_col_names if x in data.columns.values]

	# Using full or empty list as flag to see if any of such column names present
	if doc_ren_name:
		data = data.rename(columns={doc_ren_name[0]:'document'})

	if cat_ren_name:
		data = data.rename(columns={cat_ren_name[0]:'category'})

	return data

def data_preprocessing(data, token, encoder, vectorizer):
	'''
	cleansing and transformation
	'''
	data = data_evenness(data)

	# removing null values from training
	data = data.dropna()

	# basic language preprocessing
	data['document'] = data['document'].map(lambda doc: 
											preprocessing(doc, type='basic'))

	# encoder instance, saved seperately (thus fit and transform here)
	enc_inst = encoderFactory(encoder=encoder, token=token)
	data['category'] = enc_inst.fit_transform(data['category'])

	# tranformer instances
	transformers = list()

	# vectorizer instance, bigram model
	vec_inst = vectorizerFactory(vectorizer=vectorizer, 
								vectorizer_params={'ngram_range':(1,2)}, 
								token=token, data=data['document'].tolist())

	# dimensionality reducer instance
	# dim_inst = dimensionFactory(reducer='pca') 

	transformers = [('vec',vec_inst)]

	return (data, transformers)

def doc_train(data, token, encoder='label', estimator='log', 
				vectorizer='w2v_mean', validation='cv', model_save=False):
	'''
	runs training in a parallel thread, to not make user wait
	data: document data frame with categories
	token: loading saved models in the pipeline
	'''
	# data preprocessing
	data, transformers = data_preprocessing(data, token, encoder, vectorizer)
	logging.info('Data preprocessed and transformed')

	# estimator instance, delegates pipeline creation
	est_inst = estimatorFactory(estimator=estimator, token=token, 
								transformers=transformers)

	if not model_save:
		# Validation, 5-fold cross validation
		score = validateFactory(est_inst.pipeline_inst, data['document'], 
								data['category'], method=validation, 
								method_params={'cv':5})
		print ('Accuracy Score: ', score)
	else:
		# Model fit and saving
		est_inst.fit(data['document'], data['category'])
		logging.info('Model trained and stored')

def doc_predict(data, token, encoder='label', estimator='log', 
				prob_distribution=False):
	'''
	make prediction using already stored model
	data: document data frame with categories
	token: loading saved models in the pipeline
	encoder_type: for type of encoding done at time of training for targets
	estimator_type: type of estimator used at the time of training
	prob_distribution: when probabilities are required along with predictions
	'''

	# Peform prerpocessing, encoding
	# Standardized data column names
	data = data_evenness(data)

	# basic language preprocessing
	data['document'] = data['document'].map(lambda doc: 
											preprocessing(doc, type='basic'))
	logging.info('Data preprocessed')

	# Load encoder and model
	enc_inst = encoderFactory(encoder=encoder, token=token)
	est_inst = estimatorFactory(estimator=estimator, token=token)
	logging.info('Models loaded')

	# To get probability distribution back, along with results
	if prob_distribution:
		predictions = dict()
		proba_dis = est_inst.predict_proba(data['document']).to_dict()

		# Decoding labels
		classes = enc_inst.inverse_transform(list(proba_dis.keys()))
		predictions = {x:y[0] for x, y in zip(classes, proba_dis.values())}

		# Rearranging so as to put hightest at top
		predictions = sorted(predictions.items(), key=operator.itemgetter(1), 
								reverse=True)

	else:
		# First make prediction on data, then transform them back
		predictions = est_inst.predict(data['document'])
		predictions = enc_inst.inverse_transform(predictions)

	logging.info('Predictions made')
	return predictions

if __name__ == '__main__':

	# Define the parser, to read path of directorty containing images
	parser = argparse.ArgumentParser(description='Document classifier')

	# Absolute path of training file and prediction file
	parser.add_argument('--tpath', action="store", dest='tpath', default='')
	parser.add_argument('--ppath', action="store", dest='ppath', default='')
	parser.add_argument('--token', action="store", dest='token', default='')
	parser.add_argument('--save', action="store", dest='save', default=False, type=bool)

	args = parser.parse_args()

	if args.token == '':
		print ('Token required for saving and loading models during training and prediction.')
		sys.exit()

	if args.tpath == '' and args.ppath == '':
		print ('One of train or predict path needs to be provided!')
		sys.exit()

	# training
	if args.tpath != '':
		data = read_from_csv(args.tpath)
		doc_train(data, args.token, model_save=args.save)

	# prediction
	if args.ppath != '':
		data = read_from_csv(args.ppath)
		predictions = doc_predict(data, args.token)
		print (predictions)
