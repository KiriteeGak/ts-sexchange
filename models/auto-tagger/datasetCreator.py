from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import cPickle, gc
import numpy as np
from cleaner import cleaner
from utilities import *
from sklearn.linear_model import LogisticRegression as lr
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.svm import SVC
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score

ip = "localhost"
port = 27017
db = "ts-sexchange"
collection = "dse_community"
mongoCliObj = MongoClient(ip,port)[db][collection]

def createDatasetForTfidf(ret = {}):
	cursor = mongoCliObj.find({})
	for doc in cursor:
		print doc
		for tag in doc['tags']:
			if tag not in ret: ret[tag] = ''
			ret[tag] += cleaner(doc['question'])+" "
	return {k : v.strip() for k,v in ret.iteritems()}

def createDatasetForChi2(ret = {}):
	cursor = mongoCliObj.find({})
	for doc in cursor:
		for tag in doc['tags']:
			if tag not in ret: ret[tag] = []
			ret[tag].append(cleaner(doc['question']))
	return ret

def getcursor():
	return mongoCliObj.find({})

def constructTermDocMatrix():
	cursor = getcursor()
	corpus = loadFromPickle("pickleDumps/corpus_cleaned")
	labels = loadFromPickle("pickleDumps/vectorsTags")
	x_term_doc_mat = []
	y_term_doc_mat = []
	for doc in cursor:
		temp_arr_x = np.zeros(len(corpus))
		temp_arr_y = np.zeros(len(labels))
		text = cleaner(doc['question'])
		for e in text.split(' '): temp_arr_x[corpus.index(e)] = 1
		for tag in doc['tags']: temp_arr_y[labels[tag]] = 1
		x_term_doc_mat.append(temp_arr_x[:])
		y_term_doc_mat.append(temp_arr_y[:])
	return x_term_doc_mat, y_term_doc_mat

def createDatasets():
	dumpAsPickle("pickleDumps/tagstotextasstring", createDatasetForTfidf())
	dumpAsPickle("pickleDumps/tagstotextaslists", createDatasetForChi2())
	constructTermDocMatrix()
	corpus = reduce(lambda a,b : a+b, [cleaner(doc['question']).split(' ') for doc in cursor])
	dumpAsPickle("pickleDumps/corpus_cleaned",corpus)
	dumpAsPickle("pickleDumps/vectorsTags", labels)
	labels = set(list(reduce(lambda a,b: a+b, [doc['tags'] for i, doc in enumerate(cursor)])))
	labels = { e : i for i,e in enumerate(labels)}
	dumpAsPickle("pickleDumps/x_term_doc_mat",x_term_doc_mat)
	dumpAsPickle("pickleDumps/y_term_doc_mat",y_term_doc_mat)

def getcrossentropy(predicted, actual):
	cros_ent = 0
	for (pvec, avec) in zip(predicted, actual):
		p_dist = sum(avec == 1)/float(len(avec))
		for i, label in enumerate(list(avec)):
			if list(pvec)[i] == 0: cros_ent += 0
			else: cros_ent += -np.log(list(pvec)[i])*p_dist
	return cros_ent

if __name__ == '__main__':
	# Run create datasets to get the pickle files
	X = np.array(loadFromPickle("pickleDumps/x_term_doc_mat"))
	y = np.array(loadFromPickle("pickleDumps/y_term_doc_mat"))
	gc.collect()
	sss = StratifiedShuffleSplit(n_splits = 5, test_size=0.3, random_state=0)
	for hidden_neurons in range(10,100,20):
		for train_index, test_index in sss.split(X, y):
			X_train, X_test = X[train_index], X[test_index]
			y_train, y_test = y[train_index], y[test_index]
	# 		clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(hidden_neurons,), random_state=1)
	# 		clf.fit(X_train,y_train)
	# 		dumpAsPickle("mlptrained",clf)
			clf = loadFromPickle("pickleDumps/mlptrained")
			predicted = clf.predict(X_test)
			print np.shape(predicted), np.shape(y_test)
			print getcrossentropy(predicted,y_test)
			exit()