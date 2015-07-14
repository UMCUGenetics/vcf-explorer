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

        if runs.count():
            return runs
        else:
            restful.abort(404)

class Run(restful.Resource):
    def get(self, run_name):
        """
        Return run metadata from runs collection
        """
        db = get_mongodb()

        run = db.runs.find_one({'name':run_name})

        if run:
            return run
        else:
            restful.abort(404)

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

        if run_variants.alive:
            return run_variants
        else:
            restful.abort(404)

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

        if samples.alive:
            return samples
        else:
            restful.abort(404)

class Sample(restful.Resource):
    def get(self, sample_id):
        """
        Return sample metadata from run collection?
        Todo: Add metadata from samples to run collection.
        """

        db = get_mongodb()

        return {'sample':sample_id} #placeholder

class SampleVariants(restful.Resource):
    def get(self, sample_id):
        """
        Return all variants from a sample
        """
        db = get_mongodb()

        db_filter = {'samples.id':sample_id} #'samples.filter': {'$exists': False}}
        db_projection = {'chr': 1, 'pos': 1, 'ref': 1, 'alt': 1, 'samples': { '$elemMatch': { 'id': sample_id }}}

        sample_variants = db.variants.find(db_filter,db_projection)

        if sample_variants.count():
            return sample_variants
        else:
            restful.abort(404)

class Variants(restful.Resource):
    def get(self):
        """
        Return all variants
        Todo: Implement pagination?
        """
        db = get_mongodb()
        variants = db.variants.find()

        if variants.count():
            return variants
        else:
            restful.abort(404)

class Variant(restful.Resource):
    def get(self, variant_id):
        """
        Return a variant
        """
        db = get_mongodb()

        variant = db.variants.find_one({'_id':variant_id})

        if variant:
            return variant
        else:
            restful.abort(404)

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
