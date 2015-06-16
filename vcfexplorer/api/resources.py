"""
    vcfexplorer.api.resources

    VCF Explorer api resources
"""

from flask.ext import restful
import pymongo

from ..helpers import get_mongodb

class Runs(restful.Resource):
    def get(self):
        """
        Return all vcf datasets
        Todo: Implement pagination?
        """
        db = get_mongodb()
        runs = db.runs.find()
        return runs

class Run(restful.Resource):
    def get(self, run_name):
        """
        Return run data from runs collection
        """
        db = get_mongodb()

        run = db.runs.find_one({'name':run_name})

        return run

class RunVariants(restful.Resource):
    def get(self, run_name):
        """
        Return all variants from a run
        """
        db = get_mongodb()

        pipeline = [
            {"$match": {"samples.run": run_name}},
            {"$unwind": "$samples"},
            {"$match": {"samples.run": run_name}},
            {"$group": {
                "_id":"$_id",
                "samples":{"$push":"$samples"},
                "chr":{"$first":"$chr"},
                "pos":{"$first":"$pos"},
                "ref":{"$first":"$ref"},
                "alt":{"$first":"$alt"},
                }
            },
        ]
        run_variants = db.variants.aggregate(pipeline)

        return run_variants

class Samples(restful.Resource):
    def get(self):
        """
        Return all samples
        Todo: Implement pagination?
        """
        db = get_mongodb()
        pipeline = [
            {"$unwind": "$samples"},
            {"$project" :
                {"_id": 0,
                "samples": 1,
                "vcf_file": 1,
                "upload_date": 1 }
        }]
        samples = db.runs.aggregate(pipeline)
        return samples

class SampleVariants(restful.Resource):
    def get(self, sample_id):
        """
        Return all variants from a sample
        """
        db = get_mongodb()

        db_filter = {'samples.id':sample_id, 'samples.filter': {'$exists': False}}
        db_projection = {'chr': 1, 'pos': 1, 'ref': 1, 'alt': 1, 'samples': { '$elemMatch': { 'id': sample_id }}}

        sample_variants = db.variants.find(db_filter,db_projection)

        return sample_variants

class Variants(restful.Resource):
    def get(self):
        """
        Return all variants
        Todo: Implement pagination?
        """
        db = get_mongodb()
        page_size = 25
        page = 1
        variants = db.variants.find().skip(page_size*(page-1)).limit(page_size)
        return variants

class Variant(restful.Resource):
    def get(self, variant_id):
        """
        Return a variant
        """
        db = get_mongodb()

        variant = db.variants.find_one({'_id':variant_id})

        return variant

class Root(restful.Resource):
    def get(self):
        """
        Return basic database information
        """
        db = get_mongodb()
        return {
            'db': str(db),
            'mongodb version': db.command("serverStatus")['version'],
            'uptime':db.command("serverStatus")['uptime'],
        }
