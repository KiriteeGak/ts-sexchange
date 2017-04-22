import cPickle
import math, copy
import numpy as np
import time, gc
from textblob import TextBlob as tb
from sklearn.feature_selection import chi2
from utilities import *
from celery import Celery

class tfidf(object):
	def tf(self, word, blob):
		return blob.words.count(word) / len(blob.words)

	def n_containing(self, word, bloblist):
		return sum(1 for blob in bloblist if word in blob.words)

	def idf(self, word, bloblist):
		return math.log(len(bloblist) / (1 + self.n_containing(word, bloblist)))

	def tfidf(self, word, blob, bloblist):
		return self.tf(word, blob) * self.idf(word, bloblist)
		
	def pipeliner(self):
		loaded_dic = loadFromPickle('tagstotext')
		bloblist = [tb(v) for k,v in loaded_dic.iteritems()]
		for i, blob in enumerate(bloblist):
			print("Top words in document {}".format(i + 1))
			scores = {word: self.tfidf(word, blob, bloblist) for word in blob.words}
			sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
			for word, score in sorted_words[:10]:
				print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))

def createXandYHotCoding(pickle_to_load, out_string = ''):
	loaded_dic = loadFromPickle(pickle_to_load)
	y_labels = {key : i+1 for i,key in enumerate(loaded_dic.keys())}
	all_text = " ".join(loaded_dic.values())
	word_labels = {word : i+1 for i,word in enumerate(list(set(all_text.split(' '))))}
	return word_labels, y_labels

def vectoriseXandY(file_text_list, file_text_string, x_vectorised = [], y_vectorised = []):
	(word_labels, y_labels) = createXandYHotCoding(file_text_string)
	loaded_dic = loadFromPickle(file_text_list)
	for k,v in loaded_dic.iteritems():
		x_array = [[] for _ in range(len(word_labels))]
		for i,text in enumerate(v):
			already_occ = { word : 0 for word in text.split(' ')}
			for word in text.split(' '):
				if already_occ[word] == 0:
					x_array[word_labels[word]-1].append(k+"_"+str(i))
					already_occ[word] = 1
		x_vectorised.append(x_array)
		y_vectorised.append(y_labels[k])
	return x_vectorised,np.array(y_vectorised)

class chiSquareSelection():
	
	''' 
	A is the number of times that f and t cooccur
	B is the number of times that f occurs without t
	C is the number of times that t occurs without f
	D is the number of times neither t or f occur
	N is the number of observations
	'''
	
	def mainCaller(self, matrix_of_freq):
		print "started 1",
		dumpAsPickle("pickleDumps/FeatureNTerm", self.FandT(matrix_of_freq))
		print "started 2"
		dumpAsPickle("pickleDumps/FeatureNotTerm", self.FnotT(matrix_of_freq))
		print "started 3"
		dumpAsPickle("pickleDumps/notFeatureTerm", self.TnotF(matrix_of_freq))
		print "started 4"
		dumpAsPickle("pickleDumps/notFeatureNotTerm", self.notTnotFMod(matrix_of_freq))
		
	def FandT(self, matrix_of_freq):
		return [[len(c) for c in r] for r in matrix_of_freq]

	def FnotT(self, matrix_of_freq):
		ret = []
		ret = [[0 for i in range(len(matrix_of_freq[1]))] for i in range(len(matrix_of_freq))]
		for i, r in enumerate(matrix_of_freq):
			for j, ele in enumerate(r):
				e = []
				for lis in r: e += lis
				ret[i][j] = len(set(e)-set(ele))
		print np.shape(ret)
		return ret

	def TnotF(self, matrix_of_freq):
		ret = []
		ret = [[0 for i in range(len(matrix_of_freq[1]))] for i in range(len(matrix_of_freq))]
		modified_mat = zip(*matrix_of_freq)
		for i, r in enumerate(matrix_of_freq):
			for j, ele in enumerate(r):
				e = []
				for lis in list(modified_mat[j]): e += lis
				ret[i][j] = len(set(e)-set(ele))
		return ret

	# def notTnotF(self, matrix_of_freq):
	# 	ret = []
	# 	ret = [[0 for i in range(len(matrix_of_freq[1]))] for i in range(len(matrix_of_freq))]
	# 	modified_dic = self.rearrangeAsStrings(matrix_of_freq)
	# 	for i, r in enumerate(matrix_of_freq):
	# 		for j, ele in enumerate(r):
	# 			temp_dic = copy.deepcopy(modified_dic)
	# 			to_be_removed = []; li = []
	# 			ret[i][j] = self.iteratorForNotTNotF(i, j, modified_dic, temp_dic)
	# 	return ret

	def notTnotFMod(self, matrix_of_freq, all_files = [], ret = []):
		ret = [[0 for i in range(len(matrix_of_freq[1]))] for i in range(len(matrix_of_freq))]
		all_files = set(self.flattenListofLists(matrix_of_freq, dual = True)[:])
		precal = self.preCalFTDocs(matrix_of_freq)
		exit()
		loadFromPickle("pickleDumps/precalFTDocVals")
		for i, r in enumerate(matrix_of_freq):
			for j, ele in enumerate(r):
				st = time.time()
				ret[i][j] = len(all_files - precal[str(i)+'_'+str(j)])
				print "time elapsed: ",time.time()-st, "value: ", ret[i][j]
		return ret

	def preCalFTDocs(self, matrix_of_freq, ret = {}):
		for i, r in enumerate(matrix_of_freq):
			for j, ele in enumerate(r):
				print i,j
				row = self.flattenListofLists(r)
				col = self.flattenListofLists(self.getColumn(matrix_of_freq,j))
				ret[str(i)+'_'+str(j)] = set(row+col)
				print i,j, ret[str(i)+'_'+str(j)]
				exit()
		# ret = { str(i)+'_'+str(j) : set(self.flattenListofLists(r) + self.flattenListofLists(self.getColumn(matrix_of_freq,j))) for i, r in enumerate(matrix_of_freq) for j, ele in enumerate(r) }
		dumpAsPickle('pickleDumps/precalFTDocVals', ret)
		print len(ret.keys()),ret['10_0']
		return ret

	def getColumn(self, matrix, i):
		return [row[i] for row in matrix]

	def singleReduce(self, lists):
		return reduce(lambda a,b:a+b, lists)

	def flattenListofLists(self, list_of_list, dual = False, count = 0):
		# if count % 142400 == 0:
		# 	print "Hooray %d" %(count/7120)
		if dual:
			return self.singleReduce(self.singleReduce(list_of_list))
		else:
			return self.singleReduce(list_of_list)

if __name__ == '__main__':
	# uncomment this to run tf-idf
	# tfidf().pipeliner()
	# Vectorisation for word and label vectors
	X,y = vectoriseXandY("pickleDumps/tagstotextaslists","pickleDumps/tagstotextasstring")
	print "Done"
	# print chiSquareSelection().singleReduce(chiSquareSelection().singleReduce(x))
	# chiSquareSelection().mainCaller(X)
	# x = [[['1','2'],['2','4']],[['5','6'],['7','2']],[['3','6'],['4','5']]]
	print chiSquareSelection().notTnotFMod(X)