from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import cPickle
import numpy as np
from cleaner import cleaner
from utilities import *

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
	# corpus = reduce(lambda a,b : a+b, [cleaner(doc['question']).split(' ') for doc in cursor])
	# dumpAsPickle("pickleDumps/corpus_cleaned",corpus)
	# dumpAsPickle("pickleDumps/vectorsTags", labels)
	# labels = set(list(reduce(lambda a,b: a+b, [doc['tags'] for i, doc in enumerate(cursor)])))
	# labels = { e : i for i,e in enumerate(labels)}
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
	dumpAsPickle("pickleDumps/x_term_doc_mat",np.array(x_term_doc_mat))
	print "Dumping..."
	dumpAsPickle("pickleDumps/x_term_doc_mat",np.array(x_term_doc_mat))
	dumpAsPickle("pickleDumps/y_term_doc_mat",np.array(y_term_doc_mat))
	return x_term_doc_mat, y_term_doc_mat

if __name__ == '__main__':
	# dumpAsPickle("pickleDumps/tagstotextasstring", createDatasetForTfidf())
	# dumpAsPickle("pickleDumps/tagstotextaslists", createDatasetForChi2())
	constructTermDocMatrix()