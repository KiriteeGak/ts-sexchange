from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

ip = "localhost"
port = 27017
db = "ts-sexchange"
collection = "dse_community"
mongoCliObj = MongoClient(ip,port)[db][collection]