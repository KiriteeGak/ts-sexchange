from baseconfigs import *
from grabbers.communitygrabber import scrapDetails as scd
import time, os
from models.autotagger.utilities import *
from models.autotagger.predictDoc import *

while conn is True:
	community = "stats"
	comm_page_url = "https://"+community+".stackexchange.com/questions?page="+str(init_page_no)+"&sort=newest"
	curr_list += scd().returnDetails(scd().getSoup(comm_page_url))
	for dic in curr_list:
		print dic['question'], "\n",getAllTags(dic['question'])
	conn = False