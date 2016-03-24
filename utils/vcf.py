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
                        variants, variants_samples = gatk_line(line, vcf_metadata)
                        for variant_i, variant in enumerate(variants):
                            variant_id = '{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'])
                            bulk_variants.find({'_id':variant_id}).upsert().update({
                                '$push': {'samples': {'$each': variants_samples[variant_i]}},
                                '$set': variant,
                                }
                            )

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
                        bulk_variants = db.variants.initialize_unordered_bulk_op()
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
    #external_ids = fields[2].split(',')
    gt_format = fields[8].split(':')
    variants = []
    variants_samples = []
    ### Adjust pos if alt and ref bases are the same? -> indel
    ### See minimal representation from exac: https://github.com/konradjk/exac_browser/blob/master/utils.py

    ## Different variant per alt allele
    # How to handle 1/2 variants?
    # https://github.com/samtools/hts-specs/issues/77
    alt_alleles = fields[4].split(',')
    for alt_i, alt_allele in enumerate(alt_alleles):
        variant = {
            'chr': fields[0],
            'pos' : int(fields[1]),
            'ref' : fields[3],
            'alt' : alt_allele,
        }
        #variant['qual'] = fields[5];

        ## Parse external database id's
        ### Split per alternative allele?
        #for external_id in external_ids:
            #if external_id.startswith('rs'):
                #variant['dbSNP'] = external_id

        variants.append(variant)

        ## Parse samples
        variant_samples = []
        for sample_i, sample in enumerate(vcf_metadata['samples']):
            sample_gt_data = fields[9+sample_i].split(':')
            if(sample_gt_data[0] != './.' and sample_gt_data[0] != '0/0'):
                sample_gt_data = split_genotype_field(sample_gt_data, gt_format, alt_i)

                if sample_gt_data[0] != "0/*":
                    sample_var = {}
                    sample_var['genotype'] = convert_data(dict(zip(gt_format, sample_gt_data)), vcf_metadata['FORMAT'])
                    sample_var['sample'] = sample
                    sample_var['vcf_id'] = vcf_metadata['_id']

                    if fields[6] == "PASS" or fields[6] ==".":
                        pass
                    else: #Variant is filtered
                        sample_var['filter'] = fields[6]
                    variant_samples.append(sample_var)

        variants_samples.append(variant_samples)
    return variants, variants_samples

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
        if data[id] != ".":
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

def split_genotype_field(gt_data, gt_format, alt_index, allele_symbol = '*'):
    """
    Split genotype field
    """
    for gt_i, gt_field in enumerate(gt_data):
        gt_key = gt_format[gt_i]

        if gt_key == 'GT': # For now only parse GT and AD also change PL?
            gt = gt_field.split('/') #probably should add phased variant split |
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
            # Adjust the genotype
            gt_data[gt_i] = '{0}/{1}'.format(ref, alt)

        elif gt_key == 'AD':
            if gt_field != ".":
                ad = gt_field.split(',')
                gt_data[gt_i] = ','.join([ad[0],ad[alt_index]])
    return gt_data
