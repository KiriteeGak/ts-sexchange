import cPickle
import math
from textblob import TextBlob as tb
from sklearn.feature_selection import chi2

def loadFromPickle(filename):
	with open(filename+".pkl", 'rb') as fid:
		return cPickle.load(fid)

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

class chiSquareSelection():
	def getAllWords():
		loaded_dic = loadFromPickle('tagstotext')
		allWordList += {k : v.split(' ') for k,v in loaded_dic.iteritems()}
		return allWordList

	''' 
	A is the number of times that f and t cooccur
	B is the number of times that f occurs without t
	C is the number of times that t occurs without f
	D is the number of times neither t or f occur
	N is the number of observations
	'''

	def FAndT(list_of_texts_dic, list_of_all_terms_dic, ret = {}):
		for term in list_of_all_terms_dic:
			if term not in ret: ret[term] = 0
				for docs in list_of_texts:
					if term in docs.split(' '): ret[term] += 1
		return ret

	def FNotT(list_of_texts, list_of_all_terms, ret = {}):
		for term in list_of_all_terms:
			if term not in ret: ret[term] = 0
				for docs in list_of_texts:
					if term not in docs.split(' '): ret[term] += 1
		return ret

	def TNotF(list_of_texts, list_of_all_terms, ret = {}):
		for term in list_of_all_terms_dic:
			if term not in ret: ret[term] = 0
				for docs in list_of_texts:
					if term in docs.split(' '): ret[term] += 1
		return ret

	def notTNotF(list_of_texts, list_of_all_terms, ret = {}):
		for term in list_of_all_terms_dic:
			if term not in ret: ret[term] = 0
				for docs in list_of_texts:
					if term not in docs.split(' '): ret[term] += 1
		return ret

def createXs():
	pass
	
if __name__ == '__main__':
	tfidf().pipeliner()