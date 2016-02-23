"""
    vcf.py

    Utility functions to upload vcf files
"""
import re
from datetime import datetime
import sys

import pymongo
import bson

from . import connection, db
from helper import deep_update

def upload_vcf(vcf_file, vcf_type):
    """
    Parse and upload vcf files.

    """
    variant_count = 0
    bulk_variants = db.variants.initialize_unordered_bulk_op()
    vcf_name = vcf_file.split('/')[-1].replace(".vcf","")

    if db.vcfs.find({'name':vcf_name}).limit(1).count() > 0:
        sys.exit("Error: Duplicate vcf name.")

    vcf_metadata = {
        '_id': bson.objectid.ObjectId(),
        'name': vcf_name,
        'vcf_file': vcf_file,
        'upload_date' : datetime.now()
    }
    try:
        f = open(vcf_file, 'r')
    except IOError:
        print "Can't open vcf file: {0}".format(vcf_file)
    else:
        with f:
            for line in f:
                line = line.strip('\n')

                if line.startswith('#'):
                    header_line_metadata = vcf_header(line)
                    deep_update(vcf_metadata, header_line_metadata)

                else:
                    if vcf_type == 'gatk':
                        variant, variant_samples = gatk_line(line, vcf_metadata)
                        variant_id = '{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'])

                    elif vcf_type == 'delly':
                        variant, variant_samples = delly_line(line, vcf_metadata)
                        variant_id = '{}-{}-{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'], variant['CHR2'], variant['END'])

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
        db.vcfs.insert_one(vcf_metadata)

def vcf_header(line):
    """
    Parse gatk header line and return metadata dictonary
    """
    line_metadata = {}
    if line.startswith('##FILTER') or line.startswith('##ALT'):
        data = re.search('(?:##)(\w+)(?:=<ID=)(\w+)(?:,Description=")(.+)(?:">)', line).groups()
        line_metadata[data[0]] = {data[1] : data[2]}

    elif line.startswith('##INFO') or line.startswith('##FORMAT'):
        data = re.search('(?:##)(\w+)(?:=<ID=)(\w+)(?:,Number=)(.+)(?:,Type=)(\w+)(?:,Description=")(.+)(?:">)',line).groups()
        line_metadata[data[0]] = {
            data[1] : {
                'number': data[2],
                'type': data[3],
                'description': data[4]
            }
        }

    elif line.startswith('##contig'):
        data = re.search('(?:##contig=<ID=)(\w+)(?:,length=)(.+)(?:>)', line).groups()
        line_metadata['contig'] = {
            data[0] : {
                'length' : data[1]
            }
        }

    elif line.startswith('#CHROM'):
        line_metadata['samples'] = line.split()[9:]

    else:
        data = re.search('(?:##)(\w+)(?:=)(.+)',line).groups()
        line_metadata[data[0]] = data[1]

    return line_metadata

def gatk_line(line, vcf_metadata):
    fields = line.split('\t')
    external_ids = fields[2].split(',')
    gt_format = fields[8].split(':')

    ### Inmplement later: Variant per alternative allel.
    ### Adjust pos if alt and ref bases are the same?
    ### How to handle 1/2 variants?
    variant = {}
    variant['chr'] = fields[0]
    variant['pos'] = int(fields[1])
    variant['ref'] = fields[3]
    variant['alt'] = fields[4]
    #variant['qual'] = fields[5];

    #allele_counts = {
        #'total_ac': 0,
        #'alt_ac': 0,
        #'raw_total_ac': 0,
        #'raw_alt_ac': 0
    #}

    ## Parse external database id's
    for external_id in external_ids:
        if external_id.startswith('rs'):
            variant['dbSNP'] = external_id

    ## Parse samples
    variant_samples = []
    for j, sample in enumerate(vcf_metadata['samples']):
        gt_data = fields[9+j].split(':')
        if(gt_data[0] != './.' and gt_data[0] != '0/0'):
            sample_var = {}
            sample_var['genotype'] = convert_data(dict(zip(gt_format, gt_data)), vcf_metadata['FORMAT'])
            sample_var['sample'] = sample
            sample_var['vcf_id'] = vcf_metadata['_id']

            if fields[6] == "PASS" or fields[6] ==".":
                pass
                # Count alleles passed variants
                #if(gt_data[0] == '1/1'):
                    #allele_counts['alt_ac'] += 2
                    #allele_counts['raw_alt_ac'] += 2
                #elif(gt_data[0] == '0/1' or gt_data[0] == '1/0'):
                    #allele_counts['alt_ac'] += 1
                    #allele_counts['raw_alt_ac'] += 1

            else: #Variant is filtered
                sample_var['filter'] = fields[6]
                # Count alleles filtered variants
                #raw_total_allele_count += 2
                #if(gt_data[0] == '1/1'):
                    #allele_counts['raw_alt_ac'] += 2
                #elif(gt_data[0] == '0/1' or gt_data[0] == '1/0'):
                    #allele_counts['raw_alt_ac'] += 1
            variant_samples.append(sample_var)

    return variant, variant_samples

def delly_line(line, vcf_metadata):
    fields = line.split('\t')
    gt_format = fields[8].split(':')

    variant = {}
    variant['chr'] = fields[0]
    variant['chr'] = re.sub("chr","",variant['chr'],flags=re.I)
    variant['pos'] = int(fields[1])
    variant['id'] = fields[2]
    variant['ref'] = fields[3]
    variant['alt'] = fields[4]
    #variant['qual'] = fields[5];

    ## Parse info fields
    variant_info_fields = ("SVTYPE","CHR2","END","CT")
    sample_info_fields = ("PRECISE","CIEND","CIPOS","INSLEN","PE","MAPQ","CONSENSUS","SR","SRQ")

    info_fields = dict(item.split("=") for item in fields[7].split(";")[1:])
    info_fields["PRECISE"] = fields[7].split(";")[0]

    variant_info = convert_data(get_info_fields(variant_info_fields, info_fields), vcf_metadata['INFO'])
    sample_info = convert_data(get_info_fields(sample_info_fields, info_fields), vcf_metadata['INFO'])

    deep_update(variant, variant_info)
    variant['CHR2'] = re.sub("chr","",variant['CHR2'],flags=re.I)

    variant_samples = []

    for j, sample in enumerate(vcf_metadata['samples']):
        gt_data = fields[9+j].split(':')
        if (gt_data[0] != './.' and gt_data[0] != '0/0'):
            sample_var = {}
            sample_var['sample'] = sample
            sample_var['vcf_id'] = vcf_metadata['_id']
            if fields[6] != "PASS" and fields[6] !=".":
                sample_var['filter'] = fields[6]
            sample_var['genotype'] = convert_data(dict(zip(gt_format, gt_data)), vcf_metadata['FORMAT'])
            sample_var['info'] = sample_info

            variant_samples.append(sample_var)
    return variant, variant_samples

def get_info_fields(fields, info_fields):
    info = {}
    for field in fields:
        if field in info_fields:
            info[field] = info_fields[field]
    return info

def convert_data(data, metadata):
    for id in data:
        if ',' in data[id]:
            data[id] = data[id].split(',')
            if metadata[id]['type']  == "Integer":
                data[id] = map(int, data[id])
            elif metadata[id]['type']  == "Float":
                data[id] = map(float, data[id])

        else:
            if metadata[id]['type']  == "Integer":
                data[id] = int(data[id])
            elif metadata[id]['type']  == "Float":
                data[id] = float(data[id])
    return data
