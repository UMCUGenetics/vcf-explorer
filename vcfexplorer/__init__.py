#!/usr/bin/env python

from flask import Flask, g
import pymongo

from vcfexplorer import frontend, api

app = Flask(__name__)
app.register_blueprint(frontend.bp, url_prefix='/')
app.register_blueprint(api.bp, url_prefix='/api')

if __name__ == '__main__':
    app.run()
