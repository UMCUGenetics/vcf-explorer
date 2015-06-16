from flask import Blueprint
from flask_restful import Api, Resource

from resources import Runs, Run
from resources import Samples, Sample
from resources import Variants, Variant


bp = Blueprint('api', __name__)
api = Api(bp)

api.add_resource(Runs, '/runs')
api.add_resource(Run, '/runs')

api.add_resource(Samples, '/samples')
api.add_resource(Sample, '/samples')

api.add_resource(Variants, '/variants')
api.add_resource(Variant, '/variants')
