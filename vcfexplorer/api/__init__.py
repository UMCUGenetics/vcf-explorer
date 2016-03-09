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
def output_json(data, code, headers=None):
    """Dump bson to json and return response"""
    response = make_response(json_util.dumps(data))
    response.headers.extend(headers or {})
    return response

# Add api resources
api.add_resource(Root, '/')

api.add_resource(VCFs, '/vcf/')
api.add_resource(VCF, '/vcf/<string:vcf_name>')
api.add_resource(VCFVariants, '/vcf/<string:vcf_name>/variants')

api.add_resource(Samples, '/sample/')
api.add_resource(Sample, '/sample/<string:sample_name>')
api.add_resource(SampleVariants, '/sample/<string:sample_name>/variants')

api.add_resource(Variants, '/variant/')
api.add_resource(Variant, '/variant/<string:variant_id>')
