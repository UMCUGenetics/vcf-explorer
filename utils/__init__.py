
import pymongo

import config #config.py

connection = pymongo.MongoClient(host=config.MONGODB_HOST, port=config.MONGODB_PORT)
db = connection[config.MONGODB_NAME]

import database
import parse_vcf
import filter_vcf
import query
