from flask_restful import Resource
import pymongo

from ..helpers import get_mongodb, to_json

class Runs(Resource):
    """
    """
    def get(self):
        db = get_mongodb()
        runs = list(db.runs.find())
        return to_json(runs)

class Run(Resource):
    """
    """
    def get(self):
        db = get_mongodb()
        return {'run': 1}

class Samples(Resource):
    """
    """
    def get(self):
        db = get_mongodb()
        pipeline = [
            {"$unwind": "$samples"},
            {"$project" :
                {"_id": 0,
                "samples": 1,
                "vcf_file": 1,
                "upload_date": 1 }
            }
            ]
        samples = list(db.runs.aggregate(pipeline))
        return to_json(samples)

class Sample(Resource):
    """
    """
    def get(self):
        db = get_mongodb()
        return {'sample': 1}

class Variants(Resource):
    """
    """
    def get(self):
        db = get_mongodb()
        page_size = 25
        page = 1
        variants = list(db.variants.find().skip(page_size*(page-1)).limit(page_size))
        return to_json(variants)

class Variant(Resource):
    """
    """
    def get(self):
        db = get_mongodb()
