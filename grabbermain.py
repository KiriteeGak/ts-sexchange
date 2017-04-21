from baseConfigs import *

def bulkPush(list_of_docs):
	[mongoCliObj.insert(doc) for doc in list_of_docs]

while conn is True:
	try:
		community = "stats"
		comm_page_url = "https://"++".stackexchange.com/questions?page="+str(init_page_no)+"&sort=newest"
		curr_list += scd().returnDetails(scd().getSoup(comm_page_url))
		init_page_no += 1
		if init_page_no%10 == 0: bulkPush(curr_list)
		curr_list = []
	except TypeError:
		bulkPush(curr_list)
		conn = False