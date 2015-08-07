"""
    utils.py

    Utility functions used in manage.py
"""

import re
from datetime import datetime
import sys

import pymongo

connection = pymongo.MongoClient("mongodb://localhost")

### Metadata regular expressions
filter_re = re.compile('(?:##FILTER=<ID=)(\w+)(?:,Description=")(.+)(?:">)')

def upload_vcf(vcf_file):
    """
    Parse and upload vcf file.

    Todo: Parse sample metadata available in vcf?
    """
    db = connection.vcf_explorer
    variants = db.variants
    runs = db.runs

    run_name = vcf_file.split('/')[-1]
    run_name = run_name.replace(".vcf","")

    if runs.find({'name':run_name}).limit(1).count() > 0:
        sys.exit("Error: Duplicate vcf.")

    with open(vcf_file, 'r') as f:

        filters = {}
        variant_count = 0
        bulk_variants = variants.initialize_unordered_bulk_op()

        for line in f:
            line = line.strip('\n')

            if line.startswith('##FILTER'):
                filter_data = filter_re.match(line).groups()
                filters[filter_data[0]] = filter_data[1]
                continue

            if line.startswith('##'):
                continue

            elif line.startswith('#'):
                samples = line.split()[9:]
                for sample in samples:
                    if runs.find({'samples':sample}).limit(1).count() > 0:
                        sys.exit("Error: Duplicate sample.")

            # Parse variants
            fields = line.split('\t')

            ### Skip variants with length > 1 bp and/or variants with multiple alts.
            ### Only for development / testing
            if (len(fields[3]) > 1 or len(fields[4]) > 1):
                continue

            gt_format = fields[8].split(':')

            ### Inmplement later: Variant per alternative allel.
            ### Adjust pos if alt and ref bases are the same?
            ### How to handle 1/2 variants?
            #alts = fields[4].split(',')
            #for i, alt in enumerate(alts):

            variant = {}
            variant['chr'] = fields[0].upper()
            variant['pos'] = int(fields[1])
            variant['ref'] = fields[3]
            variant['alt'] = fields[4]
            var_id = '{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'])
            total_allele_count = 0
            raw_total_allele_count = 0
            alt_allele_count = 0
            raw_alt_allele_count = 0
            variant_samples = []

            for j, sample in enumerate(samples):
                gt_data = fields[9+j].split(':')
                if(gt_data[0] != './.'):
                    sample_var = dict(zip(gt_format, gt_data))
                    sample_var['id'] = sample
                    sample_var['run'] = run_name

                    if fields[6] == "PASS" or fields[6] ==".":
                        # Count alleles passed variants
                        total_allele_count += 2
                        raw_total_allele_count += 2
                        if(gt_data[0] == '1/1'):
                            alt_allele_count += 2
                            raw_alt_allele_count += 2
                        elif(gt_data[0] == '0/1' or gt_data[0] == '1/0'):
                            alt_allele_count += 1
                            raw_alt_allele_count += 1

                    else: #Variant is filtered
                        sample_var['filter'] = fields[6]
                        # Count alleles filtered variants
                        raw_total_allele_count += 2
                        if(gt_data[0] == '1/1'):
                            raw_alt_allele_count += 2
                        elif(gt_data[0] == '0/1' or gt_data[0] == '1/0'):
                            raw_alt_allele_count += 1
                    variant_samples.append(sample_var)

            bulk_variants.find({'_id':var_id}).upsert().update({
                '$push': {'samples': {'$each': variant_samples}},
                '$set': variant,
                '$inc': {
                    'total_ac': total_allele_count,
                    'alt_ac': alt_allele_count,
                    'raw_total_ac': raw_total_allele_count,
                    'raw_alt_ac': raw_alt_allele_count
                    }
                }
            )
            variant_count += 1
            if variant_count == 50000: #Upload variants in bulk -> benchmark?!
                bulk_variants.execute()
                bulk_variants = variants.initialize_unordered_bulk_op()
                variant_count = 0

        bulk_variants.execute() # insert remaining variants

    # Store run/vcf info in runs collection
    run = {
        'name' : run_name,
        'vcf_file' : vcf_file,
        'samples' : samples,
        'upload_date' : datetime.now(),
        'gatk' : {
            'version' : 'parse',
            'analysis_date' : 'parse',
            'filters' : filters
        }
    }
    runs.insert_one(run)

def create_indexes():
    """
    Create mongodb indexes.

    Todo: Move or copy to vcfexplorer flask app? On start of webapp -> make sure indexes are created.
    """
    db = connection.vcf_explorer
    variants = db.variants
    runs = db.runs
    runs.drop_indexes()
    runs.create_index("name")
    runs.create_index("samples")

    variants.drop_indexes()
    variants.create_index("samples.id")
    variants.create_index("samples.run")
    variants.create_index([("samples.id", pymongo.ASCENDING),("samples.filter", pymongo.ASCENDING)], sparse=True)

def resetdb():
    """
    Drop database and recreate indexes.
    """
    connection.drop_database('vcf_explorer')
    create_indexes()
