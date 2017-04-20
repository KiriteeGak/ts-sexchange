from grabbers.communityScraper import scrapDetails as scd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

ip = "localhost"
port = 27017
db = "ts-sexchange"
collection = "dse_community"
mongoCliObj = MongoClient(ip,port)[db][collection]
conn = True
init_page_no = 1
curr_list = []