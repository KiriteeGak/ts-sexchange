from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import cPickle
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

if __name__ == '__main__':
	dumpAsPickle("pickleDumps/tagstotextasstring", createDatasetForTfidf())
	dumpAsPickle("pickleDumps/tagstotextaslists", createDatasetForChi2())