"""
    vcfexplorer.helpers

    Helper functions for the api and frontend
"""

from flask import current_app, g, make_response
from pymongo import MongoClient

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
