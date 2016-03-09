"""
    vcfexplorer.frontend.views

    VCF Explorer frontend views
"""

from flask import send_file

from . import bp

@bp.route('/', defaults={'path': ''})
@bp.route('<path:path>') ## For now redirect everything, probably should use hardcoded paths to generate valid 404, especialy for api calls.
def index(path):
    return send_file('frontend/templates/index.html')
