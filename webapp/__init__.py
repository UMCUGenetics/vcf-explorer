#!/usr/bin/env python

from flask import Flask, g
import pymongo

app = Flask(__name__)
app.config.update(
    MONGODB_HOST='localhost',
    MONGODB_PORT=27017,
    MONGODB_NAME='vcf_explorer',
)

def connect_db():
    """
    Connect to the database specified in the app config
    """
    connection = pymongo.MongoClient(host=app.config['MONGODB_HOST'], port=app.config['MONGODB_PORT'])
    return connection[app.config['MONGODB_NAME']]

def get_db():
    """
    Get or open database connection for the current application context
    """
    if not hasattr(g, 'mongodb_conn'):
        g.mongodb_conn = connect_db()
    return g.mongodb_conn


import webapp.views
import webapp.utils

if __name__ == '__main__':
    app.run()
