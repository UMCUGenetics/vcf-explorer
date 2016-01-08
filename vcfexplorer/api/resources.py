"""
    vcfexplorer.api.resources

    VCF Explorer api resources
"""

from flask.ext.restful import Api, Resource, abort, reqparse
import pymongo

from ..helpers import get_mongodb

class Runs(Resource):
    def get(self):
        """
        Return all vcf datasets
        """
        db = get_mongodb()
        runs = db.vcfs.find()

        if runs.count():
            return runs
        else:
            abort(404)

class Run(Resource):
    def get(self, run_name):
        """
        Return run metadata from runs collection
        """
        db = get_mongodb()

        run = db.vcfs.find_one({'name':run_name})

        if run:
            return run
        else:
            abort(404)

class RunVariants(Resource):
    def __init__(self):
        """
        Setup argument parsing
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('filtered_vars', type = bool, default = False)
        super(RunVariants, self).__init__()

    def get(self, run_name):
        """
        Return all variants from a run
        """
        args = self.reqparse.parse_args()
        db = get_mongodb()

        pipeline = [
            {"$match": {"samples.run": run_name}},
            {"$unwind": "$samples"},
            {"$match": {"samples.run": run_name}},
        ]

        if not args['filtered_vars']:
            pipeline.extend([
                {"$match": {"samples.filter": {"$exists": False}}}
            ])

        pipeline.extend([
            {"$group": {
                "_id":"$_id",
                "samples": {"$push":"$samples"},
                "chr": {"$first":"$chr"},
                "pos": {"$first":"$pos"},
                "ref": {"$first":"$ref"},
                "alt": {"$first":"$alt"},
                "filter": {"$first":"$samples.filter"},
                "total_ac": {"$first":"$total_ac"},
                "alt_ac": {"$first":"$alt_ac"},
                }
            }
        ])

        run_variants = db.variants.aggregate(pipeline, allowDiskUse=True)

        if run_variants.alive:
            return run_variants
        else:
            abort(404)

class Samples(Resource):
    def get(self):
        """
        Return all samples
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
        samples = db.vcfs.aggregate(pipeline)

        if samples.alive:
            return samples
        else:
            abort(404)

class Sample(Resource):
    def get(self, sample_id):
        """
        Return sample metadata from run collection?
        """

        db = get_mongodb()
        run = db.vcfs.find_one({'samples':sample_id})

        if run:
            return {'sample':sample_id, 'run': run}
        else:
            abort(404)

class SampleVariants(Resource):
    def __init__(self):
        """
        Setup argument parsing
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('filtered_vars', type = bool, default = False)
        super(SampleVariants, self).__init__()

    def get(self, sample_id):
        """
        Return all variants from a sample
        """
        args = self.reqparse.parse_args()
        db = get_mongodb()

        db_filter = {'samples.id':sample_id}
        if not args['filtered_vars']:
            db_filter['samples.filter'] = {'$exists': False}

        db_projection = {
            'chr': 1, 'pos': 1, 'ref': 1, 'alt': 1,
            'total_ac': 1, 'alt_ac': 1,
            'samples': { '$elemMatch': {'id':sample_id} }
        }

        sample_variants = db.variants.find(db_filter, db_projection)

        if sample_variants.count():
            return sample_variants
        else:
            abort(404)

class Variants(Resource):
    def get(self):
        """
        Return all variants
        """
        db = get_mongodb()

        db_projection = {
            '_id': 1,
            'chr': 1, 'pos': 1, 'ref': 1, 'alt': 1,
            'total_ac': 1, 'alt_ac': 1,
        }

        variants = db.variants.find(projection=db_projection)

        if variants.count():
            return variants
        else:
            abort(404)

class Variant(Resource):
    def get(self, variant_id):
        """
        Return a variant
        """
        db = get_mongodb()

        db_projection = {
            '_id': 1,
            'chr': 1, 'pos': 1, 'ref': 1, 'alt': 1,
            'total_ac': 1, 'alt_ac': 1,
            'raw_total_ac':1, 'raw_alt_ac': 1,
            'dbSNP': 1,
        }

        variant = db.variants.find_one({'_id':variant_id}, db_projection)

        if variant:
            return variant
        else:
            abort(404)

class Root(Resource):
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
