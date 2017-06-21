"""Utility functions to filter vcf files."""
import sys

import vcf as py_vcf

from . import db


def filter_sv_vcf(vcf_file, flank=500):
    """
    Parse vcf files and filter on database.

    Args:
        vcf_file (str): Path to vcf file
    """
    # Open vcf file
    try:
        vcf = py_vcf.Reader(open(vcf_file, 'r'))
    except IOError:
        sys.exit("Can't open vcf file: {0}".format(vcf_file))
    else:
        # setup filter
        db_filter = py_vcf.parser._Filter('DB', 'Similar variant found in database with {0}bp flank'.format(flank))
        vcf.filters[db_filter[0]] = db_filter
        vcf.infos['DB_Count'] = py_vcf.parser._Info('DB_Count', 1, 'Int', 'Variant count in database', 'vcf_explorer', '0.1')
        vcf.infos['DB_Frequency'] = py_vcf.parser._Info('DB_Frequency', 1, 'Float', 'Variant frequency in database', 'vcf_explorer', '0.1')

        # output
        vcf_writer = py_vcf.Writer(sys.stdout, vcf)

        # Count number of samples in db for frequency
        query_aggregate = [
            {'$unwind': '$samples'},
            {'$group': {'_id': None, 'uniqueSamples': {'$addToSet': '$samples'}}},
            {'$count': 'samples_in_db'}
        ]
        sampels_in_db = len(db.vcfs.distinct('samples'))

        # Filter per record
        for record in vcf:
            # DEL DUP INV INS filter
            if record.INFO['SVTYPE'] in ['DEL', 'DUP', 'INV', 'INS']:
                query_aggregate = [
                    {'$match': {
                        'chr': record.CHROM,
                        'pos': {'$gte': record.POS-flank, '$lte': record.POS+flank},
                        'info.END': {'$gte': record.INFO['END']-flank, '$lte': record.INFO['END']+flank},
                        'info.SVTYPE': record.INFO['SVTYPE'],
                        '$or': [
                            {'samples.sample': {'$nin': vcf.samples}},
                            {'samples.1': {'$exists': True}}
                        ]
                    }},
                    {'$unwind': '$samples'},
                    {'$count': 'samples_with_variant'}
                ]
                variant_aggregate = list(db.variants.aggregate(query_aggregate))

                db_count = 0
                db_frequency = 0.0
                if variant_aggregate:
                    record.add_filter(db_filter[0])
                    db_count = variant_aggregate[0]['samples_with_variant']
                    db_frequency = float(variant_aggregate[0]['samples_with_variant']) / sampels_in_db

                record.add_info('DB_Count', db_count)
                record.add_info('DB_Frequency', db_frequency)
                vcf_writer.write_record(record)

            # BND filter
            # Change this when bnd is parsed on input
            elif record.INFO['SVTYPE'] == "BND":
                breakpoint = record.ALT[0]
                query = {
                    'chr': record.CHROM,
                    'pos': {'$gte': record.POS-flank, '$lte': record.POS+flank},
                    'bnd_info.chr': breakpoint.chr,
                    'bnd_info.pos': {'$gte': breakpoint.pos-flank, '$lte': breakpoint.pos+flank},
                    '$or': [
                        {'samples.sample': {'$nin': vcf.samples}},
                        {'samples.1': {'$exists': True}}
                    ]
                }
                variant = db.variants.find_one(query)
                # Test speed: db.variants.find(query).limit(1).count(True)
                if variant:
                    record.add_filter(db_filter[0])
                vcf_writer.write_record(record)
