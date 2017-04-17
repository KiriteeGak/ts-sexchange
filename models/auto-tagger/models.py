import cPickle
import math
from textblob import TextBlob as tb

def loadFromPickle(filename):
	with open(filename+".pkl", 'rb') as fid:
		return cPickle.load(fid)

def tf(word, blob):
	return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
	return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
	return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
	return tf(word, blob) * idf(word, bloblist)
	
def taggerModel():
	pass

def pipeliner():
	loaded_dic = loadFromPickle('tagstotext')
	bloblist = [tb(v) for k,v in loaded_dic.iteritems()]
	for i, blob in enumerate(bloblist):
		print("Top words in document {}".format(i + 1))
		scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
		sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
		for word, score in sorted_words[:3]:
			print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))

if __name__ == '__main__':
	pipeliner()