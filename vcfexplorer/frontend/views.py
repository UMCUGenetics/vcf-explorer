"""
    vcfexplorer.frontend.views

    VCF Explorer frontend views
"""

from flask import render_template

from . import bp

@bp.route('/')
def hello_world():
    return 'hello_world'

@bp.route('runs/')
def runs():
    return render_template('runs.html')

@bp.route('samples/')
def samples():
    return render_template('samples.html')

@bp.route('variants/')
def variants():
    return render_template('variants.html')
