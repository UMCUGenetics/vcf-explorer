"""
    vcfexplorer.api.resources

    VCF Explorer api resources
"""

from flask.ext.restful import Api, Resource, abort, reqparse
import pymongo

from ..helpers import get_mongodb

## Common argument parsing
common_reqparse = reqparse.RequestParser()
common_reqparse.add_argument('limit', type = int, default = 1)
common_reqparse.add_argument('offset', type = int, default = 0)

common_reqparse.add_argument('sort_field', type = str, default = '')
common_reqparse.add_argument('sort_order', type = int, default = 1)

class VCFs(Resource):
    def get(self):
        """
        Return all vcf datasets
        """
        db = get_mongodb()
        vcfs = db.vcfs.find()

        if vcfs.count():
            return vcfs
        else:
            abort(404)

class VCF(Resource):
    def get(self, vcf_name):
        """
        Return run metadata from vcfs collection
        """
        db = get_mongodb()

        vcf = db.vcfs.find_one({'name':vcf_name})

        if vcf:
            return vcf
        else:
            abort(404)

class VCFVariants(Resource):
    def __init__(self):
        """
        Setup argument parsing
        """
        self.reqparse = common_reqparse.copy()
        self.reqparse.add_argument('filtered_vars', type = bool, default = False)
        super(VCFVariants, self).__init__()

    def get(self, vcf_name):
        """
        Return all variants from a run
        """
        args = self.reqparse.parse_args()
        db = get_mongodb()
        vcf = db.vcfs.find_one({'name':vcf_name})

        if vcf:
            pipeline = [
                {"$match": {"samples.vcf_id": vcf['_id']}},
                {"$unwind": "$samples"},
                {"$match": {"samples.vcf_id": vcf['_id']}},
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
                    #"filter": {"$first":"$samples.filter"},
                    #"total_ac": {"$first":"$total_ac"},
                    #"alt_ac": {"$first":"$alt_ac"},
                    }
                }
            ])

            vcf_variants = db.variants.aggregate(pipeline, allowDiskUse=True)

            if vcf_variants.alive:
                return vcf_variants
            else:
                abort(404)
        else: # if vcf
            abort(404)

class Samples(Resource):
    def __init__(self):
        """
        Setup argument parsing
        """
        self.reqparse = common_reqparse.copy()
        super(Samples, self).__init__()

    def get(self):
        """
        Return all samples
        """
        args = self.reqparse.parse_args()
        db = get_mongodb()

        pipeline = [
            {"$unwind": "$samples"}
        ]

        if args['sort_field']:
            pipeline.append({"$sort": {args['sort_field']: args['sort_order']} })

        pipeline.extend([
            {"$skip": args['offset']},
            {"$limit": args['limit']},
            {"$group": {
                "_id": "$samples",
                "vcf_files": {"$push": "$vcf_file"},
                "upload_date": {"$last": "$upload_date"}
                }
            }
        ])
        print pipeline
        samples = db.vcfs.aggregate(pipeline)

        if samples.alive:
            return samples
        else:
            abort(404)

class Sample(Resource):
    def get(self, sample_name):
        """
        Return sample metadata from run collection?
        """

        db = get_mongodb()
        vcfs = db.vcfs.find({'samples':sample_name})
        if vcfs:
            vcfs = [vcf for vcf in vcfs]
            return {'sample':sample_name, 'vcfs': vcfs}
        else:
            abort(404)

class SampleVariants(Resource):
    def __init__(self):
        """
        Setup argument parsing
        """
        self.reqparse = common_reqparse.copy()
        self.reqparse.add_argument('filtered_vars', type = bool, default = False)
        super(SampleVariants, self).__init__()

    def get(self, sample_name):
        """
        Return all variants from a sample
        """
        args = self.reqparse.parse_args()
        db = get_mongodb()
        print sample_name
        db_filter = {'samples.sample':sample_name}
        if not args['filtered_vars']:
            db_filter['samples.filter'] = {'$exists': False}

        db_projection = {
            'chr': 1, 'pos': 1, 'ref': 1, 'alt': 1,
            #'total_ac': 1, 'alt_ac': 1,
            'samples': { '$elemMatch': {'sample':sample_name} }
        }

        sample_variants = db.variants.find(db_filter, db_projection)

        if sample_variants.count():
            return sample_variants
        else:
            abort(404)

class Variants(Resource):
    def __init__(self):
        """
        Setup argument parsing
        """
        self.reqparse = common_reqparse.copy()
        super(Variants, self).__init__()

    def get(self):
        """
        Return all variants
        """
        args = self.reqparse.parse_args()
        db = get_mongodb()

        db_projection = {
            'samples' : 0
        }

        variants = db.variants.find(projection=db_projection, skip=args['offset'], limit=args['limit'])

        ## Sorting
        if args['sort_field']:
            variants = variants.sort(args['sort_field'],args['sort_order'])

        if variants.count():
            return [variants, variants.count()]
        else:
            abort(404)

class Variant(Resource):
    def get(self, variant_id):
        """
        Return a variant
        """
        db = get_mongodb()

        db_projection = {
            'samples' : 0
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
