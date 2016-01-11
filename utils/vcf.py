"""
    vcf.py

    Utility functions to upload vcf files
"""
import re
from datetime import datetime
import sys

import pymongo

from . import connection, db
from helper import deep_update

def upload_vcf(vcf_file, vcf_type):
    """
    Parse and upload vcf files.

    """
    variant_count = 0
    bulk_variants = db.variants.initialize_unordered_bulk_op()
    run_name = vcf_file.split('/')[-1].replace(".vcf","")

    if runs.find({'name':run_name}).limit(1).count() > 0:
        sys.exit("Error: Duplicate vcf.")

    vcf_metadata = {
        'run': run_name,
        'vcf': vcf_file
    }

    with open(vcf_file, 'r') as f:
        for line in f:
            line = line.strip('\n')

            if line.startswith('#'):
                if vcf_type == 'gatk':
                    header_line_metadata = gatk_header(line)
                    deep_update(vcf_metadata, header_line_metadata)
                elif vcf_type == 'delly':
                    header_line_metadata = delly_header(line)
                    deep_update(vcf_metadata, header_line_metadata)

            else:
                if vcf_type == 'gatk':
                    variant, variant_samples = gatk_line(line, vcf_metadata)
                    variant_id = '{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'])

                elif vcf_type == 'delly':
                    variant, variant_samples = delly_line(line, vcf_metadata)
                    #variant_id

                bulk_variants.find({'_id':variant_id}).upsert().update({
                    '$push': {'samples': {'$each': variant_samples}},
                    '$set': variant,
                    }
                )
                variant_count += 1
                if variant_count == 10000:
                    bulk_variants.execute()
                    bulk_variants = variants.initialize_unordered_bulk_op()
                    variant_count = 0

        bulk_variants.execute() # insert remaining variants

        # Store run/vcf metadata in vcfs collection
        run = {
            'name' : run_name,
            'vcf_file' : vcf_file,
            'samples' : vcf_metadata['samples'],
            'upload_date' : datetime.now(),
        }
        db.vcfs.insert_one(run)

def gatk_header(line):
    """
    Parse gatk header line and return metadata dictonary
    """
    line_metadata = {}
    if line.startswith('##FILTER'):
        filter_re = re.compile('(?:##FILTER=<ID=)(\w+)(?:,Description=")(.+)(?:">)')
        filter_data = filter_re.match(line).groups()
        line_metadata['header'] = {'filter':{filter_data[0] : filter_data[1]}}

    elif line.startswith('#CHROM'):
        line_metadata['samples'] = line.split()[9:]

    return line_metadata

def gatk_line(line, vcf_metadata):
    fields = line.split('\t')
    external_ids = fields[2].split(',')
    gt_format = fields[8].split(':')

    ### Inmplement later: Variant per alternative allel.
    ### Adjust pos if alt and ref bases are the same?
    ### How to handle 1/2 variants?

    variant = {}
    variant['chr'] = fields[0].upper()
    variant['pos'] = int(fields[1])
    variant['ref'] = fields[3]
    variant['alt'] = fields[4]

    total_allele_count = 0
    raw_total_allele_count = 0
    alt_allele_count = 0
    raw_alt_allele_count = 0

    ## Parse external database id's
    for external_id in external_ids:
        if external_id.startswith('rs'):
            variant['dbSNP'] = external_id

    # Parse samples
    variant_samples = []
    for j, sample in enumerate(vcf_metadata['samples']):
        gt_data = fields[9+j].split(':')
        if(gt_data[0] != './.' and gt_data[0] != '0/0'):
            sample_var = dict(zip(gt_format, gt_data))
            sample_var['id'] = sample
            sample_var['run'] = vcf_metadata['run']

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

    return variant, variant_samples

def delly_header(line):
    """
    Parse delly header line and return metadata dictonary
    """
    line_metadata = {}
    re_match = re.search("##(\w+)=<ID=(\w+),Number=(\w+),Type=(\w+),Description=\"(.+)\">",line)
    if re_match:
        line_metadata['header'] = {re_match.group(1).upper() : [] }
        line_metadata['header'][re_match.group(1).upper()].append({"id": re_match.group(2), "number": re_match.group(3), "type": re_match.group(4), "description": re_match.group(5)})
    else:
        re_match = re.search("##(\w+)=<ID=(\w+),Description=\"(.+)\">",line)
        if re_match:
            line_metadata['header'] = {re_match.group(1).upper() : [] }
            line_metadata['header'][re_match.group(1).upper()].append({"id": re_match.group(2), "description":re_match.group(3)})
        else:
            re_match = re.search("##(\w+)=(.+)",line)
            if re_match:
                line_metadata[re_match.group(1).upper()] = re_match.group(2)
    return line_metadata

def delly_line(line, vcf_metadata):
    variant = {}
    variant_info_fields = ("svtype","chr2","end","ct")
    sample_info_fields = ("precise","ciend","cipos","inslen","pe","mapq","consensus","sr","srq")

    fields = line.split('\t')

    gt_format = fields[8].split(':')
    info_fields = dict(item.split("=") for item in fields[7].split(";")[1:])
    info_fields["precise"] = fields[7].split(";")[0]

    #vcf['caller'] = info_fields['svmethod'] -> this should be parsed from header lines if possible.

    variant_info = get_info_fields(variant_info_fields, info_fields)
    sample_info = get_info_fields(sample_info_fields, info_fields)

    variant['chr'] = fields[0].upper()
    variant['chr'] = re.sub("chr","",variant['chr'],flags=re.i)
    variant['pos'] = int(fields[1])
    variant['id'] = fields[2]
    variant['ref'] = fields[3]
    variant['alt'] = fields[4]
    variant['qual'] = fields[5];
    variant['variant_info'] = variant_info
    variant['variant_info']['chr2'] = re.sub("chr","",variant['variant_info']['chr2'],flags=re.i)

    for id in variant['variant_info']:
        if search_header(id, vcf_metadata['header']['info'])[0]['type'] == "integer" and re.match("^-*\d+$",str(variant['variant_info'][id])):
            variant['variant_info'][id] = int(variant['variant_info'][id])
        if search_header(id, vcf_metadata['header']['info'])[0]['type'] == "float" and re.match("^-*(\d+)\.*(\d*)$",str(variant['variant_info'][id])):
            variant['variant_info'][id] = float(variant['variant_info'][id])

    variant_samples = []

    for j, sample in enumerate(vcf_metadata['samples']):
        gt_data = fields[9+j].split(':')
        if (gt_data[0] != './.' and gt_data[0] != '0/0'):
            sample_var = {}
            sample_var['name'] = sample
            sample_var['filter'] = fields[6]
            sample_var['format'] = dict(zip(gt_format, gt_data))
            sample_var['info'] = sample_info

        for id in sample_var['format']:
            if search_header(id, vcf_metadata['header']['format'])[0]['type'] == "integer" and re.match("^-*\d+$",str(sample_var['format'][id])):
                sample_var['format'][id] = int(sample_var['format'][id])
            if search_header(id, vcf_metadata['header']['format'])[0]['type'] == "float" and re.match("^-*(\d+)\.*(\d*)$",str(sample_var['format'][id])):
                sample_var['format'][id] = float(sample_var['format'][id])

        for id in sample_var['info']:
            if search_header(id, vcf_metadata['header']['info'])[0]['type'] == "integer" and re.match("^-*\d+$",str(sample_var['info'][id])):
                sample_var['info'][id] = int(sample_var['info'][id])
            if search_header(id, vcf_metadata['header']['info'])[0]['type'] == "float" and re.match("^-*(\d+)\.*(\d*)$",str(sample_var['info'][id])):
                sample_var['info'][id] = float(sample_var['info'][id])
        variant_samples.append(sample_var)
    return variant, variant_samples

def get_info_fields(fields, info_fields):
    info = {}
    for field in fields:
        if field in info_fields:
            info[field] = info_fields[field]
    return info

def search_header(id, d):
    return [element for element in d if element['id'] == id]
