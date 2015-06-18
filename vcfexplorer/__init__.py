"""
    vcfexplorer

    VCF Explorer application package
"""

from flask import Flask

from . import frontend, api

app = Flask(__name__, static_folder=None)
app.config.from_object('config')

app.register_blueprint(frontend.bp, url_prefix='/')
app.register_blueprint(api.bp, url_prefix='/api')

if __name__ == '__main__':
    app.run()
