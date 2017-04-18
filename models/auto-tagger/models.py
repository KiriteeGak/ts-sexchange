import cPickle
import math
import numpy as np
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

def createXandYHotCoding(pickle_to_load, out_string = ''):
	loaded_dic = loadFromPickle(pickle_to_load)
	y_labels = {key : i+1 for i,key in enumerate(loaded_dic.keys())}
	all_text = " ".join([v for v in loaded_dic.values()])
	word_labels = {word: i+1 for i,word in enumerate(list(set(all_text.split(' '))))}
	return word_labels, y_labels

def vectoriseXandY(file_text_list, file_text_string, x_vectorised = [], y_vectorised = []):
	(word_labels, y_labels) = createXandYHotCoding(file_text_string)
	loaded_dic = loadFromPickle(file_text_list)
	for k,v in loaded_dic.iteritems():
		for text in v:
			x_array = np.zeros(len(word_labels))
			y_array = y_labels[k]
			for word in text.split(' '):
				x_array[word_labels[word]] = 1
			x_vectorised.append(np.array(x_array))
			y_vectorised.append(y_array)

if __name__ == '__main__':
	# tfidf().pipeliner()
	vectoriseXandY("tagstotextaslists","tagstotextasstring")