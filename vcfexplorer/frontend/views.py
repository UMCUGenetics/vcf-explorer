"""
    vcfexplorer.frontend.views

    VCF Explorer frontend views
"""

from flask import render_template

from . import bp

@bp.route('/')
def hello_world():
    return render_template('index.html')
