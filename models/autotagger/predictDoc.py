from utilities import *
from cleaner import *
import numpy as np

class MLP(object):
	def predictADoc(self, document):
		corpus = loadFromPickle("models/autotagger/pickleDumps/corpus_cleaned")
		docvec = np.zeros(len(corpus))
		text = cleaner(document)
		for e in text.split(' '): 
			try: docvec[corpus.index(e)] = 1
			except ValueError: pass
		clf = loadFromPickle("models/autotagger/pickleDumps/mlptrained_10_Ns")
		predicted = clf.predict_proba(docvec.reshape(1,-1))
		return predicted

	def getcrossentropy(self, predicted, actual):
		cros_ent = 0
		for (pvec, avec) in zip(predicted, actual):
			p_dist = sum(avec == 1)/float(len(avec))
			for i, label in enumerate(list(avec)): 
				if list(pvec)[i] > 0: cros_ent += -np.log(list(pvec)[i])*float(p_dist)
		return cros_ent

	def getIndices(self, arr, n):
		return [i for i,x in enumerate(list(arr)) if x == n]

	def getIndicesOfTopNEles(self, arr, n, add_up = False):
		if not add_up:
			return arr.argsort()[-1*n:][::-1]
		indices_by_sum = [np.where(arr == x) for i, x in enumerate(list(np.sort(arr)[::-1])) if sum(list(arr)[:i]) <= 95]
		indices_by_ele = self.getIndicesOfTopNEles(arr,2)
		if len(indices_by_sum) <= len(indices_by_ele):
			return indices_by_sum
		return indices_by_ele

	def getresults(self, predicted, actual):
		labels = loadFromPickle("models/autotagger/pickleDumps/vectorsTags")
		vec2ques = loadFromPickle("models/autotagger/pickleDumps/vec2ques")
		len_inte = 0; base_len = 0
		for (pvec, avec) in zip(predicted, actual):
			ind1 = self.getIndices(avec, 1)
			ind2 = self.getIndicesOfTopNEles(pvec, len(ind1))
			(l1a,l2p) = zip(*[(labels.keys()[labels.values().index(t1)], labels.keys()[labels.values().index(t2)]) for (t1,t2) in zip(ind1,ind2)])
			len_inte += len(set(l1a).intersection(set(l2p))); base_len += len(l1a);
		return len_inte/float(base_len)

	def getmaxLabelsFromNN(self, predicted_probs):
		ind = self.getIndicesOfTopNEles(predicted_probs[0],0,add_up = True)
		labels = loadFromPickle("models/autotagger/pickleDumps/vectorsTags")
		return [labels.keys()[labels.values().index(i)] for i in ind]

	def tagaDoc(self, doc):
		return self.getmaxLabelsFromNN(self.predictADoc(doc))

class textBasedExtraction(object):
	def matchTags(self, ques):
		labels = loadFromPickle("models/autotagger/pickleDumps/vectorsTags")
		question_label = []
		for label in labels:
			if len(set(cleaner(ques).split(' ')).intersection(cleaner(label, base = False).split(' '))) == len(cleaner(label, base = False).split(' ')):
				score = self.maxMatchScore(label, ques)
				question_label.append(label)
			elif len(label.split(' ')) >= 2:
				score = self.maxMatchScore(label, ques)
				if score > 0.75: 
					question_label.append(label)
		return question_label

	def maxMatchScore(self, label, text):
		num = len("".join(list(set(cleaner(label, base = False).split(' ')).intersection(set(cleaner(text).split(' '))))))
		den = len("".join(cleaner(label, base= False)))
		return num/float(den)

def getAllTags(doc):
	return MLP().tagaDoc(doc), textBasedExtraction().matchTags(doc)