from grabbers.communitygrabber import scrapDetails as scd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

ip = "localhost"
port = 27017
db = "ts-sexchange"
collection = "stats_community"
mongoCliObj = MongoClient(ip,port)[db][collection]
conn = True
init_page_no = 1
error_connections = 0
curr_list = []