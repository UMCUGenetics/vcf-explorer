
import pymongo

connection = pymongo.MongoClient("mongodb://localhost")
db = connection.vcf_explorer

import database
import parse_vcf
import filter_vcf
import query
