"""
    vcfexplorer.frontend.views

    VCF Explorer frontend views
"""

from flask import send_file

from . import bp

@bp.route('/', defaults={'path': ''})
@bp.route('<path:path>')
def index(path):
    return send_file('frontend/templates/index.html')
