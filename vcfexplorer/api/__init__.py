from flask import Blueprint
from flask_restful import Api, Resource

from resources import HelloWorld
from resources import Runs

bp = Blueprint('api', __name__)
api = Api(bp)

api.add_resource(HelloWorld, '/hello')

api.add_resource(Runs, '/runs')
