from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from collections import Counter
import timestring

ip = "localhost"
port = 27017
db = "ts-sexchange"
collection = "dse_community"
mongoCliObj = MongoClient(ip,port)[db][collection]

for c in mongoCliObj.find({}):
	try:
		mongoCliObj.update({'_id': c['_id']} , { '$set' : {'date_of_posting' : c['time_of_posting'].split(' ')[0].replace('-','')}},False,False)
	except (AttributeError, DuplicateKeyError) as e:
		pass