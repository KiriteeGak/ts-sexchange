from baseconfigs import *
from grabbers.communitygrabber import scrapDetails as scd
import time
import os
from models.autotagger.utilities import *

def bulkPush(list_of_docs):
	for doc in list_of_docs:
		try:
			mongoCliObj.insert(doc)
		except DuplicateKeyError as e:
			pass

if os.path.isfile('temp/page_scraped.pkl'):	
	init_page_no == loadFromPickle('temp/page_scraped.pkl')

while conn is True:
	try:
		community = "stats"
		comm_page_url = "https://"+community+".stackexchange.com/questions?page="+str(init_page_no)+"&sort=newest"
		time.sleep(1)
		curr_list += scd().returnDetails(scd().getSoup(comm_page_url))
		print "On page %d with number of question crawled as %d" %(init_page_no, init_page_no*50)
		init_page_no += 1
		if init_page_no%10 == 0: bulkPush(curr_list); curr_list = []; 
	except TypeError:
		error_connections += 1
		bulkPush(curr_list)
		if error_connections >= 10:
			dumpAsPickle('temp/page_scraped', init_page_no)
			init_page_no += 1
			conn = False