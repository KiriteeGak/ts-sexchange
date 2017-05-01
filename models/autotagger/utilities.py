import cPickle

def dumpAsPickle(filename, toDump):
	with open(filename+".pkl", 'wb') as fid:
		cPickle.dump(toDump, fid, protocol = 2)

def loadFromPickle(filename):
	with open(filename+".pkl", 'rb') as fid:
		return cPickle.load(fid)