from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from collections import Counter
import itertools
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from matplotlib.pyplot import cm

ip = "localhost"
port = 27017
db = "ts-sexchange"
collection = "dse_community"

class tagTrends():
	def getAllTags(self, mongoCliObj):
		ret = []
		for doc in mongoCliObj.find({}):
			ret += doc['tags']
		return list(set(ret))

	def tagCounts(self, cursor, ret = {}):
		for doc in cursor:
			ret = dict(Counter(ret) + Counter(self.tagCountsHelper(doc['tags'])))
		return ret

	def tagCountsHelper(self, list_of_tags):
		return {tag : 1 for tag in list_of_tags}

	def fillRemainingTags(self, mongoCliObj , tags_mentioned):
		ret = {}
		all_tags = self.getAllTags(mongoCliObj)
		for tag in all_tags:
			if tag not in tags_mentioned:
				ret[tag] = 0
				continue
			ret[tag] = tags_mentioned[tag]
		return ret

	def getMentionedTags(self, cursor):
		return self.tagCounts(cursor)

	def mainTrends(self, mongoCliObj, cursor):
		return self.fillRemainingTags(mongoCliObj, self.getMentionedTags(cursor))

	def getTimeDates(self, min_rev_date = 20140513, start_dates = [], end_dates = [], curr_rev_date = datetime.now().date()):
		while int(str(curr_rev_date).replace('-','')) > int(min_rev_date):
			start_dates.append(str(curr_rev_date).replace('-',''))
			end_dates.append(str((curr_rev_date-timedelta(days = 30))).replace('-',''))
			curr_rev_date = curr_rev_date-timedelta(days = 30)
		return start_dates, end_dates

	def mongoDatewiseextract(self, sd, ed, mongoCliObj):
		cursor = mongoCliObj.find({'date_of_posting':{'$lte':sd, '$gt': ed}})
		ret = self.mainTrends(mongoCliObj,cursor)
		return ret

	def countsModifiedl2d(self, tag_freq_per_period, all_tags):
		ret = {}
		for tag in all_tags:
			ret[tag] = []
			for dic in tag_freq_per_period:
				ret[tag].append(dic[tag])
		return ret

class plotter(object):
	def plotgraph(self, data, number_of_top_tags = 5):
		for i, each in enumerate(data):
			if i < number_of_top_tags:
				plot_lines = getRegressionLine(list(reversed(each[1])))
				plt.plot(plot_lines,label=each[0])
			else:
				plt.xlabel('Time'); plt.ylabel('No. of questions asked')
				plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=4, fancybox=True, shadow=True)
				plt.show()
				exit()

def getRegressionLine(pts):
	return np.poly1d(np.polyfit(np.arange(len(pts)), np.array(pts), 1))

if __name__ == '__main__':
	mongoCliObj = MongoClient(ip,port)[db][collection]
	selist, edlist = tagTrends().getTimeDates()
	dic_of_tag_freq = [tagTrends().mongoDatewiseextract(d,edlist[i],mongoCliObj).copy() for i,d in enumerate(selist)]
	modified_freq_by_tags = tagTrends().countsModifiedl2d(dic_of_tag_freq,tagTrends().getAllTags(mongoCliObj))
	sorted_freq = sorted(modified_freq_by_tags.items(), key = lambda items: sum(np.array(items[1])), reverse = True)
	plotter().plotgraph(sorted_freq)