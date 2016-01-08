"""
    vcf.py

    Utility functions to upload vcf files
"""
import re
from datetime import datetime
import sys

from . import connection

def upload_vcf(vcf_file, vcf_type):
    """
    Parse and upload vcf files.

    """

    if vcf_type == 'gatk':
        upload_gatk(vcf_file)
    elif vcf_type == 'delly':
        upload_delly(vcf_file)

def upload_gatk(vcf_file):
    filter_re = re.compile('(?:##FILTER=<ID=)(\w+)(?:,Description=")(.+)(?:">)')

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

            ## Parse external database id's
            external_ids = fields[2].split(',')
            for external_id in external_ids:
                if external_id.startswith('rs'):
                    variant['dbSNP'] = external_id

            ## Parse samples
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
            if variant_count == 10000: #Upload variants in bulk -> benchmark?!
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

def upload_delly(vcf_file):
    vcf = {}
    filename = vcf_file.split("/")[-1]
    vcf['FILENAME'] = filename
    vcf['HEADER'] = {}

    with open(vcf_file, 'r') as f:
        variant_count = 0
        bulk_variants = variants.initialize_unordered_bulk_op()
        for line in f:
            line = line.strip('\n')
            if line.startswith('##'):
                vcf = v.delly_header(line, vcf)
                continue
            elif line.startswith('#'):
                samples = line.split()[9:]
                vcf['SAMPLES'] = samples
                continue

            variant, variant_samples, vcf = v.delly_line(line, vcf, samples)
            if variant and variant_samples:
                bulk_variants.find({'CHR':variant['CHR'],'POS':variant['POS'],
                    'VARIANT_INFO.SVTYPE':variant['VARIANT_INFO']['SVTYPE'],
                    'VARIANT_INFO.CHR2':variant['VARIANT_INFO']['CHR2'],
                    'VARIANT_INFO.END':variant['VARIANT_INFO']['END'],
                    'VARIANT_INFO.CT':variant['VARIANT_INFO']['CT']}).upsert().update({
                    '$push': {'SAMPLES': {'$each': variant_samples}},
                    '$set': variant,
                })
                variant_count += 1
            if variant_count == 10000: #Upload variants in bulk -> benchmark?!
                bulk_variants.execute()
                bulk_variants = variants.initialize_unordered_bulk_op()
                variant_count = 0
    bulk_variants.execute()
    bulk_vcfs = vcfs.initialize_unordered_bulk_op()
    bulk_vcfs.find( { 'FILENAME':vcf['FILENAME'], 'FILEFORMAT':vcf['FILEFORMAT'],'FILEDATE':vcf['FILEDATE'] } ).upsert().update({'$set': vcf})
    bulk_vcfs.execute()

def delly_header(line, vcf):
    re_match = re.search("##(\w+)=<ID=(\w+),Number=(\w+),Type=(\w+),Description=\"(.+)\">",line)
    if re_match:
        if re_match.group(1).upper() not in vcf['HEADER']:
            vcf['HEADER'][re_match.group(1).upper()] = []
            vcf['HEADER'][re_match.group(1).upper()].append({"ID": re_match.group(2), "NUMBER": re_match.group(3), "TYPE": re_match.group(4), "DESCRIPTION": re_match.group(5)})

    else:
        re_match = re.search("##(\w+)=<ID=(\w+),Description=\"(.+)\">",line)
        if re_match:
            if re_match.group(1).upper() not in vcf['HEADER']:
                vcf['HEADER'][re_match.group(1).upper()] = []
                vcf['HEADER'][re_match.group(1).upper()].append({"ID": re_match.group(2), "DESCRIPTION":re_match.group(3)})
        else:
            re_match = re.search("##(\w+)=(.+)",line)
            if re_match:
                vcf[re_match.group(1).upper()] = re_match.group(2)
    return vcf

def get_info_fields(fields, info_fields):
    info = {}
    for field in fields:
        if field in info_fields:
            info[field] = info_fields[field]
    return info

def search_header(id, d):
    return [element for element in d if element['ID'] == id]

def delly_line(line, vcf, samples):
    variant = {}
    variant_info_fields = ("SVTYPE","CHR2","END","CT")
    sample_info_fields = ("PRECISE","CIEND","CIPOS","INSLEN","PE","MAPQ","CONSENSUS","SR","SRQ")

    fields = line.split('\t')

    gt_format = fields[8].split(':')
    info_fields = dict(item.split("=") for item in fields[7].split(";")[1:])
    info_fields["PRECISE"] = fields[7].split(";")[0]

    vcf['CALLER'] = info_fields['SVMETHOD']

    variant_info = get_info_fields(variant_info_fields, info_fields)
    sample_info = get_info_fields(sample_info_fields, info_fields)

    variant['CHR'] = fields[0].upper()
    variant['CHR'] = re.sub("CHR","",variant['CHR'],flags=re.I)
    variant['POS'] = int(fields[1])
    variant['ID'] = fields[2]
    variant['REF'] = fields[3]
    variant['ALT'] = fields[4]
    variant['QUAL'] = fields[5];
    variant['VARIANT_INFO'] = variant_info
    variant['VARIANT_INFO']['CHR2'] = re.sub("CHR","",variant['VARIANT_INFO']['CHR2'],flags=re.I)

    for id in variant['VARIANT_INFO']:
        if search_header(id, vcf['HEADER']['INFO'])[0]['TYPE'] == "Integer" and re.match("^-*\d+$",str(variant['VARIANT_INFO'][id])):
            variant['VARIANT_INFO'][id] = int(variant['VARIANT_INFO'][id])
        if search_header(id, vcf['HEADER']['INFO'])[0]['TYPE'] == "Float" and re.match("^-*(\d+)\.*(\d*)$",str(variant['VARIANT_INFO'][id])):
            variant['VARIANT_INFO'][id] = float(variant['VARIANT_INFO'][id])

    variant_samples = []

    for j, sample in enumerate(samples):
        gt_data = fields[9+j].split(':')
        if (gt_data[0] != './.' and gt_data[0] != '0/0'):
            sample_var = {}
            sample_var['NAME'] = sample
            sample_var['FILTER'] = fields[6]
            sample_var['FORMAT'] = dict(zip(gt_format, gt_data))
            sample_var['INFO'] = sample_info

        for id in sample_var['FORMAT']:
            if search_header(id, vcf['HEADER']['FORMAT'])[0]['TYPE'] == "Integer" and re.match("^-*\d+$",str(sample_var['FORMAT'][id])):
                sample_var['FORMAT'][id] = int(sample_var['FORMAT'][id])
            if search_header(id, vcf['HEADER']['FORMAT'])[0]['TYPE'] == "Float" and re.match("^-*(\d+)\.*(\d*)$",str(sample_var['FORMAT'][id])):
                sample_var['FORMAT'][id] = float(sample_var['FORMAT'][id])

        for id in sample_var['INFO']:
            if search_header(id, vcf['HEADER']['INFO'])[0]['TYPE'] == "Integer" and re.match("^-*\d+$",str(sample_var['INFO'][id])):
                sample_var['INFO'][id] = int(sample_var['INFO'][id])
            if search_header(id, vcf['HEADER']['INFO'])[0]['TYPE'] == "Float" and re.match("^-*(\d+)\.*(\d*)$",str(sample_var['INFO'][id])):
                sample_var['INFO'][id] = float(sample_var['INFO'][id])
        variant_samples.append(sample_var)
    return variant, variant_samples, vcf
