import cPickle, math, copy, time, gc
import numpy as np
from textblob import TextBlob as tb
from sklearn.feature_selection import chi2
from utilities import *
from datasetCreator import *
from cleaner import *

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

	def notTnotFMod(self, matrix_of_freq, all_files = [], ret = []):
		ret = [[0 for i in range(len(matrix_of_freq[1]))] for i in range(len(matrix_of_freq))]
		all_files = set(self.flattenListofLists(matrix_of_freq, dual = True)[:])
		precal = self.preCalFTDocs(matrix_of_freq)
		loadFromPickle("pickleDumps/precalFTDocVals")
		for i, r in enumerate(matrix_of_freq):
			for j, ele in enumerate(r):
				ret[i][j] = len(all_files - precal[str(i)+'_'+str(j)])
				print "time elapsed: ",time.time()-st, "value: ", ret[i][j]
		return ret

	def preCalFTDocs(self, matrix_of_freq, ret = {}):
		ret = { str(i)+'_'+str(j) : set(self.flattenListofLists(r,i,j) + self.flattenListofLists(self.getColumn(matrix_of_freq,j),i,j)) for i, r in enumerate(matrix_of_freq) for j, ele in enumerate(r) }
		dumpAsPickle('pickleDumps/precalFTDocVals', ret)
		return ret

	def getColumn(self, matrix, i):
		return [row[i] for row in matrix]

	def singleReduce(self, lists):
		return reduce(lambda a,b:a+b, lists)

	def flattenListofLists(self, list_of_list, i=1, j=1, dual = False):
		ret = []
		if dual:
			for r in list_of_list:
				for cell in r:
					ret += cell
			return ret
		for r in list_of_list:
			ret += r
		return ret

class trainNN(object):
	def MLPdocvec(self):
		X = np.array(loadFromPickle("pickleDumps/x_term_doc_mat"))
		y = np.array(loadFromPickle("pickleDumps/y_term_doc_mat"))
		sss = StratifiedShuffleSplit(n_splits = 5, test_size=0.3, random_state=0)
		for hidden_neurons in range(10,100,25):
			gc.collect()
			for train_index, test_index in sss.split(X, y):
				X_train, X_test = X[train_index], X[test_index]
				y_train, y_test = y[train_index], y[test_index]
				clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(hidden_neurons,), random_state=1)
				clf.fit(X_train,y_train)
				dumpAsPickle("pickleDumps/mlptrained_"+str(hidden_neurons)+"_Ns",clf)
				clf = loadFromPickle("pickleDumps/mlptrained_"+str(hidden_neurons)+"_Ns")
				predicted = clf.predict_proba(X_test)
				print self.getcrossentropy(predicted,y_test), self.getresults(predicted, y_test)
				print "Pass done at neuron number %d" %(hidden_neurons)

# if __name__ == '__main__':
	# tfidf().pipeliner()
	# X,y = vectoriseXandY("pickleDumps/tagstotextaslists","pickleDumps/tagstotextasstring")
	# chiSquareSelection().mainCaller(X)
	# Run createdatasets to get the pickle files
	# createDatasets()
	# MLP().MLPdocvec()
	# dumpAsPickle("pickleDumps/wordmatchquestions",textBasedExtraction(getcursor()).matchTags())