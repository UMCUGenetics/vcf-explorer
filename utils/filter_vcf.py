"""
    parse_vcf.py

    Utility functions to filter vcf files
"""
import sys

import pymongo
import vcf as py_vcf

from . import connection, db

def filter_sv_vcf(vcf_file, flank=500):
    """
    Parse vcf files and filter on database

    Args:
        vcf_file (str): Path to vcf file
    """
    #Open vcf file
    try:
        vcf = py_vcf.Reader(open(vcf_file, 'r'))
    except IOError:
        sys.exit("Can't open vcf file: {0}".format(vcf_file))
    else:
        #setup filter
        db_filter = py_vcf.parser._Filter('DB','Similar variant found in database with {0}bp flank'.format(flank))
        vcf.filters[db_filter[0]] = db_filter

        #output
        vcf_writer = py_vcf.Writer(sys.stdout, vcf)

        #Filter per record
        for record in vcf:
            if record.INFO['SVTYPE'] in ['DEL','DUP','INV','INS']:
                query = {
                    'chr': record.CHROM,
                    'pos': {'$gte': record.POS-flank, '$lte': record.POS+flank},
                    'info.END': {'$gte': record.INFO['END']-flank, '$lte': record.INFO['END']+flank},
                    'info.SVTYPE': record.INFO['SVTYPE'],
                    '$or':[
                        {'samples.sample' : {'$nin': vcf.samples}},
                        {'samples.1': {'$exists': True}}
                    ]
                }
                variant = db.variants.find_one(query)
                if variant:
                    record.add_filter(db_filter[0])
                    vcf_writer.write_record(record)
                else:
                    vcf_writer.write_record(record)
            #else : #BND
