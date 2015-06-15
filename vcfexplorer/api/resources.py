from flask_restful import Resource
import pymongo

from ..helpers import get_mongodb

class HelloWorld(Resource):
    def get(self):
        return {'print':'Hello World!'}

class Runs(Resource):
    def get(self):
        db = get_mongodb()
        runs = list(db.runs.find())
        return runs
