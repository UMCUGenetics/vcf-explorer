"""
    vcfexplorer.api

    VCF Explorer api package
"""

from flask import Blueprint, make_response
from flask.ext import restful
from bson import json_util

from .resources import Root
from .resources import VCFs, VCF, VCFVariants
from .resources import Samples, Sample, SampleVariants
from .resources import Variants, Variant

bp = Blueprint('api', __name__)

api = restful.Api(bp)

# Modify api json representation
@api.representation('application/json')
def output_json(data, code, headers):
    """Dump bson to json and return response"""
    response = make_response(json_util.dumps(data), code)
    response.headers.extend(headers)
    return response

# Add api resources
api.add_resource(Root, '/')

api.add_resource(VCFs, '/vcfs/')
api.add_resource(VCF, '/vcfs/<string:vcf_name>')
api.add_resource(VCFVariants, '/vcfs/<string:vcf_name>/variants')

api.add_resource(Samples, '/samples/')
api.add_resource(Sample, '/samples/<string:sample_name>')
api.add_resource(SampleVariants, '/samples/<string:sample_name>/variants')

api.add_resource(Variants, '/variants/')
api.add_resource(Variant, '/variants/<string:variant_id>')
