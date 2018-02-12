"""
    parse_vcf.py

    Utility functions to upload vcf files
"""
import re
import sys
import pymongo
import bson
import json

import vcf as py_vcf
from datetime import datetime
from helper import deep_update

from . import connection, db

def upload_vcf(vcf_file):
    """
    Parse vcf files and upload variants using bulk functionality of mongodb.

    Args:
        vcf_file (str): Path to vcf file
        vcf_template (str): Path to json template
    """

    vcf_name = vcf_file.split('/')[-1].replace(".vcf","")
    if db.vcfs.find({'name':vcf_name}).limit(1).count(True):
        sys.exit("Error: Duplicate vcf name.")

    # Setup bulk upload variables
    variant_count = 0
    bulk_variants = db.variants.initialize_unordered_bulk_op()

    #Open vcf file
    try:
        vcf = py_vcf.Reader(open(vcf_file, 'r'))
    except IOError:
        sys.exit("Can't open vcf file: {0}".format(vcf_file))
    else:
        # Setup vcf metadata dictonary, upload to vcfs collection
        vcf_metadata = {
            '_id': bson.objectid.ObjectId(),
            'name': vcf_name,
            'vcf_file': vcf_file,
            'samples': vcf.samples,
            'upload_date' : datetime.now(),
            'info':{},
            'format':{},
            'filter':{},
            'metadata': dict(vcf.metadata)
        }

        # Store vcf metadata (from header)
        for info in vcf.infos:
            vcf_metadata['info'][info] = {'num':vcf.infos[info].num,'desc':vcf.infos[info].desc}
        for gt_format in vcf.formats:
            vcf_metadata['format'][gt_format] = {'num':vcf.formats[gt_format].num,'desc':vcf.formats[gt_format].desc}
        for filter in vcf.filters:
            vcf_metadata['filter'][filter] = vcf.filters[filter].desc

        # Convert all dot in metadata keys for compatibility with mongodb
        vcf_metadata = convert_dict_keys(vcf_metadata, dot_to_underscore)

        # Parse variant records
        for record in vcf:
            variants, variants_samples = parse_vcf_record(record, vcf_metadata)
            for variant_i, variant in enumerate(variants):
                #Setup variant id based on vcf_type
                if record.is_snp or record.is_indel:
                    variant_id = '{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'])
                elif record.is_sv:
            variant_id = '{}-{}-{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['chr2'], variant['end'], variant['orientation'], variant['remoteOrientation'])

        if variants_samples[variant_i]:
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

def parse_vcf_record(vcf_record, vcf_metadata):
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
        if vcf_record.is_sv:
        chr, pos, ref, alt, chr2, end, svlen, svtype, orientation, remoteOrientation = parse_sv_record( vcf_record, alt_index, alt_allele )
        variant = {
        'chr' : chr,
        'pos' : pos,
        'ref' : ref,
        'alt' : alt,            
        'chr2' : chr2,
        'end' : end,
        'svlen' : svlen,
        'svtype' : svtype,
        'orientation' : orientation,
        'remoteOrientation': remoteOrientation,
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
                    sample_var['info'] = vcf_record.INFO
                    if 'CIPOS' in vcf_record.INFO:
                sample_var['info']['POS_RANGE'] = [ pos+vcf_record.INFO['CIPOS'][0], pos+vcf_record.INFO['CIPOS'][1] ]
            else:
                sample_var['info']['POS_RANGE'] = [ pos, pos ]
                    if 'CIEND' in vcf_record.INFO:
                sample_var['info']['END_RANGE'] = [ end+vcf_record.INFO['CIEND'][0], end+vcf_record.INFO['CIEND'][1] ]
            else:
                sample_var['info']['END_RANGE'] = [ end, pos ]

                    # Set filter field
                    if vcf_record.FILTER:
                        sample_var['filter'] = vcf_record.FILTER

                    variant_samples.append(sample_var)

        variants_samples.append(variant_samples)
    return variants, variants_samples

def parse_sv_record( vcf_record, alt_index, alt_allele ):

    pos, ref, alt = get_minimal_representation(vcf_record.POS, str(vcf_record.REF), str(alt_allele))
        chr = vcf_record.CHROM
        
    # If sv is a breakend
    if ( isinstance(vcf_record.ALT[0], py_vcf.model._Breakend) ) :
        breakpoint = vcf_record.ALT[alt_index]
        chr2 = breakpoint.chr
        end = breakpoint.pos
        alt = breakpoint.connectingSequence
        orientation = breakpoint.orientation
        remoteOrientation = breakpoint.remoteOrientation
    else:
        if 'CHR2' in vcf_record.INFO:
            chr2 = vcf_record.INFO['CHR2']
        else:
            chr2 = vcf_record.CHROM
        if 'END' in vcf_record.INFO:
            end = vcf_record.INFO['END']
        else:
            sys.exit("Cannot find 'END' in info field")
    if vcf_record.CHROM == chr2:
        svlen = end-pos
    else:
        svlen = False
    if 'SVTYPE' in vcf_record.INFO:
        svtype = vcf_record.INFO['SVTYPE']
    else:
        sys.exit("Cannot find 'SVTYPE' in info field")
    if svtype == 'DEL':
        orientation = False
        remoteOrientation = True
    elif svtype == 'INS':
        orientation = False
        remoteOrientation = True
    elif svtype == 'DUP':
        orientation = True
        remoteOrientation = False
    elif svtype == 'INV':
        if 'INV5' in vcf_record.INFO:
            orientation = True
            remoteOrientation = True
        elif 'INV3' in vcf_record.INFO:
            orientation = False
            remoteOrientation = False
        else:
            sys.exit("Unknown inversion orientation")
    elif svtype != 'BND':
        sys.exit("Cannot convert orientation and remoteOrientation")
    
    return chr, pos, ref, alt, chr2, end, svlen, svtype, orientation, remoteOrientation


def get_info_fields(record_info, info_fields):
    """
    Get info fields from pyvcf record_info

    Args:
        record_info (pyvcf record infos): info fields from vcf record
        info_fields (list): info to get from record_info

    Returns:
        info (dict): Info dictionary containing requested info fields
    """
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

        elif genotype_field == 'AD':
            gt_data[genotype_field] = [sample_call[genotype_field][i] for i in [0,alt_index+1]]
        else: # Correct other (all) entries for alt index!
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

def convert_dict_keys(obj, convert):
    """
    Recursively goes through the dictionary obj and replaces keys with the convert function.
    Args:
        obj (dict): dictonary to be converted
        convert (func): convert function to apply on dictonary keys
    """
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = convert_dict_keys(v, convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(convert_dict_keys(v, convert) for v in obj)
    else:
        return obj
    return new

def dot_to_underscore(string):
    """
    Replace every dot with an underscore in a string.
    """
    return string.replace('.','_')


