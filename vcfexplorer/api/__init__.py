"""
    vcfexplorer.api

    VCF Explorer api package
"""

from flask import Blueprint, make_response
from flask.ext import restful
from bson import json_util

from resources import Root
from resources import Runs, Run, RunVariants
from resources import Samples, SampleVariants
from resources import Variants, Variant

bp = Blueprint('api', __name__)

api = restful.Api(bp)

# Modify api json representation
@api.representation('application/json')
def output_json(data, code, headers=None):
    """
    Dump bson to json and return response
    """
    response = make_response(json_util.dumps(data))
    response.headers.extend(headers or {})
    return response

# Add api resources
api.add_resource(Root, '/')

api.add_resource(Runs, '/runs')
api.add_resource(Run, '/runs/<string:run_name>')
api.add_resource(RunVariants, '/runs/<string:run_name>/variants')

api.add_resource(Samples, '/samples')
api.add_resource(SampleVariants, '/samples/<string:sample_id>')

api.add_resource(Variants, '/variants')
api.add_resource(Variant, '/variants/<string:variant_id>')
