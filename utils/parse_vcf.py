"""
    parse_vcf.py

    Utility functions to upload vcf files
"""
import re
from datetime import datetime
import sys

import pymongo
import vcf as py_vcf
import bson
import json

from . import connection, db
from helper import deep_update

def upload_vcf(vcf_file, vcf_template):
    """
    Parse and upload vcf files in bulk.

    Args:
        vcf_file (str): Path to vcf file
    """
    vcf_name = vcf_file.split('/')[-1].replace(".vcf","")
    # Setup bulk upload variables
    variant_count = 0
    bulk_variants = db.variants.initialize_unordered_bulk_op()

    if db.vcfs.find({'name':vcf_name}).limit(1).count() > 0:
        sys.exit("Error: Duplicate vcf name.")

    try:
        f = open(vcf_template, 'r')
    except IOError:
        print "Can't open vcf template file: {0}".format(vcf_template)
    else:
        with f:
            vcf_template = json.load(f)

    try:
        vcf = py_vcf.Reader(open(vcf_file, 'r'))
    except IOError:
        print "Can't open vcf file: {0}".format(vcf_file)
    else:
        # Setup vcf metadata dictonary, upload to vcfs collection
        vcf_metadata = {
            '_id': bson.objectid.ObjectId(),
            'name': vcf_name,
            'vcf_file': vcf_file,
            'upload_date' : datetime.now(),
            'info':{},
            'format':{},
            'filter':{},
            'metadata': dict(vcf.metadata)
        }
        for info in vcf.infos:
            vcf_metadata['info'][info] = {'num':vcf.infos[info].num,'desc':vcf.infos[info].desc}
        for gt_format in vcf.formats:
            vcf_metadata['format'][gt_format] = {'num':vcf.formats[gt_format].num,'desc':vcf.formats[gt_format].desc}
        for filter in vcf.filters:
            vcf_metadata['filter'][filter] = vcf.filters[filter].desc

        # Parse variant records
        for record in vcf:
            variants, variants_samples = parse_vcf_record(record, vcf_metadata, vcf_template)
            for variant_i, variant in enumerate(variants):
                #Setup variant id based on vcf_type
                if vcf_template['vcf_type'] == 'SNP':
                    variant_id = '{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'])
                elif vcf_template['vcf_type'] == 'SV':
                    variant_id = '{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'])

                bulk_variants.find({'_id':variant_id}).upsert().update({
                    '$push': {'samples': {'$each': variants_samples[variant_i]}},
                    '$set': variant,
                    }
                )
            variant_count += len(variants)

            # Upload variants in bulk
            if variant_count >= 10000:
                bulk_variants.execute()
                bulk_variants = db.variants.initialize_unordered_bulk_op()
                variant_count = 0

        # insert remaining variants and insert vcf metadata to vcfs collection
        bulk_variants.execute()
        db.vcfs.insert_one(vcf_metadata)

def parse_vcf_record(vcf_record, vcf_metadata, vcf_template):
    """
    Parse vcf variant record.
    VCF variants records containing multiple alternative alleles are splitted by alternative allele and
    get a minimal (left aligned) representation. Sample information (e.g. genotype)
    is added to seperate list of sample dictionaries to be able to update exisiting variants.

    Args:
        vcf_record (pyvcf record): pyvcf variant record
        vcf_metadata (dict): metadata dictonary containing vcf header data
        vcf_template (dict): vcf template dictonary
    Returns:
        list: variants, list of variant dictionaries.
        list: variants_samples, list of variant samples lists.
    """
    # Setup general variables
    variants = []
    variants_samples = []

    # Different variant per alt allele
    # 1/2 variants are splitted into two variants with genotype: 1/-
    # https://github.com/samtools/hts-specs/issues/77
    for alt_index, alt_allele in enumerate(vcf_record.ALT):
        pos, ref, alt = get_minimal_representation(vcf_record.POS, str(vcf_record.REF), str(alt_allele))
        #print vcf_template['variant_info_fields']
        variant = {
            'chr': vcf_record.CHROM,
            'pos' : pos,
            'ref' : ref,
            'alt' : alt,
            'info' : get_info_fields(vcf_record.INFO, vcf_template['variant_info_fields'])
        }
        variants.append(variant)

        # Parse samples
        variant_samples = []
        for sample_index, sample_call in enumerate(vcf_record.samples):
            # Skip variant if no or reference call.
            if sample_call.is_variant:
                sample_gt_data = adjust_genotype(sample_call, alt_index)
                if sample_gt_data['GT'] != "0/-":
                    sample_var = {}
                    sample_var['genotype'] = sample_gt_data
                    sample_var['sample'] = sample_call.sample
                    sample_var['vcf_id'] = vcf_metadata['_id']
                    sample_var['info'] = get_info_fields(vcf_record.INFO, vcf_template['sample_info_fields'])

                    # Set filter field
                    if vcf_record.FILTER:
                        sample_var['filter'] = vcf_record.FILTER

                    variant_samples.append(sample_var)

        variants_samples.append(variant_samples)
    return variants, variants_samples

def get_info_fields(record_info, info_fields):
    info = {}
    for field in info_fields:
        if field in record_info:
            info[field] = record_info[field]
    return info

def adjust_genotype(sample_call, alt_index, allele_symbol = '-'):
    """
    Adjust genotype fields by alternative allele index

    Args:
        sample_call (pyvcf CALL): sample call pyvcf record
        alt_index (int): Alternative allele index
        allele_symbol (str): replacment genotype symbol for overlapping variants
    Returns:
        gt_data (dict): Adjusted gt data

    """
    gt_data = {}
    for genotype_field in sample_call.data._fields:
        if genotype_field == 'GT':
            gt = sample_call[genotype_field].split('/')
            ref = allele_symbol
            alt = allele_symbol
            if gt[0] == gt[1]: #hom call
                ref = '1'
                alt = '1'
            else: #het call
                if (int(gt[0]) == alt_index + 1 or int(gt[1]) == alt_index + 1):
                    alt = '1'
                if (int(gt[0]) == 0 or int(gt[1]) == 0):
                    ref = '0'
            gt_data['GT'] = '{0}/{1}'.format(ref, alt)

        else: # Correct for alt index!
            gt_data[genotype_field] = sample_call[genotype_field]

    return gt_data

def get_minimal_representation(pos, ref, alt):
    """
    ExAC - MIT License (MIT)
    Copyright (c) 2014, Konrad Karczewski, Daniel MacArthur, Brett Thomas, Ben Weisburd

    Get the minimal representation of a variant, based on the ref + alt alleles in a VCF
    This is used to make sure that multiallelic variants in different datasets,
    with different combinations of alternate alleles, can always be matched directly.
    Args:
        pos (int): genomic position in a chromosome (1-based)
        ref (str): ref allele string
        alt (str): alt allele string
    Returns:
        tuple: (pos, ref, alt) of remapped coordinate
    """
    pos = int(pos)
    # If it's a simple SNV, don't remap anything
    if len(ref) == 1 and len(alt) == 1:
        return pos, ref, alt
    else:
        # strip off identical suffixes
        while(alt[-1] == ref[-1] and min(len(alt),len(ref)) > 1):
            alt = alt[:-1]
            ref = ref[:-1]
        # strip off identical prefixes and increment position
        while(alt[0] == ref[0] and min(len(alt),len(ref)) > 1):
            alt = alt[1:]
            ref = ref[1:]
            pos += 1
        return pos, ref, alt

# def convert_data(data, metadata):
#     """
#     Convert vcf data using metadata dictonary
#
#     Args:
#         data (dict): dictonary with str values
#         metadata (dict): metadata dictonary containing vcf header data needed to convert values in data dict
#     Returns:
#         data (dict): converted data dictonary
#     """
#     for id in data:
#         if data[id] != ".":
#             if ',' in data[id]:
#                 data[id] = data[id].split(',')
#                 if metadata[id]['type']  == "Integer":
#                     data[id] = map(int, data[id])
#                 elif metadata[id]['type']  == "Float":
#                     data[id] = map(float, data[id])
#
#             else:
#                 if metadata[id]['type']  == "Integer":
#                     data[id] = int(data[id])
#                 elif metadata[id]['type']  == "Float":
#                     data[id] = float(data[id])
#     return data
