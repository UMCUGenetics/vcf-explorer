"""
    vcfexplorer.frontend

    VCF Explorer frontend package
"""

from flask import Blueprint

bp = Blueprint('frontend', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='static'
)

from . import views
