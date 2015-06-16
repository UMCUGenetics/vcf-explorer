"""
    vcfexplorer.helpers

    Helper functions for the api and frontend
"""

from flask import current_app, g
from pymongo import MongoClient
import json
from bson import json_util

def connect_mongodb():
    """
    Connect to the database specified in the app config
    """
    connection = MongoClient(host=current_app.config.get('MONGODB_HOST'), port=current_app.config.get('MONGODB_PORT'))
    return connection[current_app.config.get('MONGODB_NAME')]

def get_mongodb():
    """
    Get or open database connection for the current application context
    """
    if not hasattr(g, 'mongodb_conn'):
        g.mongodb_conn = connect_mongodb()
    return g.mongodb_conn

def to_json(data):
    """
    Convert mongodb data to json
    """
    return json.dumps(data, default=json_util.default)
