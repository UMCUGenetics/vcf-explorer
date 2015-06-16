"""
    vcfexplorer.frontend

    VCF Explorer frontend package
"""

from flask import Blueprint

bp = Blueprint('frontend', __name__, template_folder='templates')

@bp.route('/')
def hello_world():
    return 'hello_world'
