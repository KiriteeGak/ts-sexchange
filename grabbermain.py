from baseconfigs import *

def bulkPush(list_of_docs):
	[mongoCliObj.insert(doc) for doc in list_of_docs]

while conn is True:
	try:
		community = "stats"
		comm_page_url = "https://"+community+".stackexchange.com/questions?page="+str(init_page_no)+"&sort=newest"
		try:
			curr_list += scd().returnDetails(scd().getSoup(comm_page_url))
		print "On page %d with number of question crawled as %d" %(init_page_no, init_page_no*50)
		init_page_no += 1
		if init_page_no%10 == 0: bulkPush(curr_list)
		curr_list = []
	except TypeError:
		bulkPush(curr_list)
		conn = False