#!/usr/bin/env python

from flask import render_template, request
import pymongo

from webapp import app, get_db
from utils import Pagination

@app.route('/')
@app.route('/runs/')
def runs():
    db = get_db()
    runs = list(db.runs.find())
    return render_template('runs.html', runs=runs)

@app.route('/runs/<run_name>', defaults={'page':1})
@app.route('/runs/<run_name>/<int:page>')
def run_view(run_name,page):
    db = get_db()
    db_filter = {'samples.run':run_name}

    page_size = 25
    pipeline = [
        {"$match": {"samples.run": run_name}},
        {"$skip": page_size*(page-1)},
        {"$limit": page_size},
        {"$unwind": "$samples"},
        {"$match": {"samples.run": run_name}},
        {"$group": {
            "_id":"$_id",
            "samples":{"$push":"$samples"},
            "chr":{"$first":"$chr"},
            "pos":{"$first":"$pos"},
            "ref":{"$first":"$ref"},
            "alt":{"$first":"$alt"},
            }
        },
    ]

    run_variants = list(db.variants.aggregate(pipeline))
    variant_count = db.variants.find(db_filter).count()

    pagination = Pagination(page, page_size, variant_count)

    run = db.runs.find_one({'name':run_name})

    return render_template('run.html', run = run, run_variants = run_variants, pagination=pagination)

@app.route('/samples/')
def samples():
    db = get_db()
    pipeline = [{"$unwind": "$samples"}, {"$project" : {"_id": 0, "samples": 1, "vcf_file": 1, "upload_date": 1 }}]
    samples = list(db.runs.aggregate(pipeline))
    return render_template('samples.html', samples = samples)

@app.route('/samples/<sample_id>', defaults={'page':1})
@app.route('/samples/<sample_id>/<int:page>')
def sample_view(sample_id, page):
    db = get_db()
    db_filter = {'samples.id':sample_id, 'samples.filter': {'$exists': False}}
    db_projection = {'chr': 1, 'pos': 1, 'ref': 1, 'alt': 1, 'samples': { '$elemMatch': { 'id': sample_id }}}

    page_size = 25
    sample_variants = db.variants.find(db_filter,db_projection).skip(page_size*(page-1)).limit(page_size)
    variant_count = sample_variants.count()

    pagination = Pagination(page, page_size, variant_count)

    return render_template('sample.html', sample = sample_id, sample_variants = sample_variants, variant_count=variant_count, pagination=pagination)

@app.route('/variants/', defaults={'page':1})
@app.route('/variants/<int:page>')
def variants(page):
    db = get_db()

    page_size = 25

    variants = db.variants.find().skip(page_size*(page-1)).limit(page_size)
    variant_count = variants.count()

    pagination = Pagination(page, page_size, variant_count)

    return render_template('variants.html', variants = variants, variant_count=variant_count, pagination=pagination)

@app.route('/variants/<variant_id>')
def variant_view(variant_id):
    db = get_db()
    variant = db.variants.find_one({'_id':variant_id})
    return render_template('variant.html', variant = variant)
