"""
    vcfexplorer.api

    VCF Explorer api package
"""

from flask import Blueprint
from flask_restful import Api, Resource

from resources import Runs, Run
from resources import Samples, Sample
from resources import Variants, Variant


bp = Blueprint('api', __name__)
api = Api(bp)

api.add_resource(Runs, '/runs')
api.add_resource(Run, '/run/<id>')# add /runs/<id>?

api.add_resource(Samples, '/samples')
api.add_resource(Sample, '/sample/<id>')# add /samples/<id>?

api.add_resource(Variants, '/variants')
api.add_resource(Variant, '/variant/<id>')# add /variants/<id>?
