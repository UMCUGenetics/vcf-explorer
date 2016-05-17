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
    Parse and upload vcf files in bulk.

    Args:
        vcf_file (str): Path to vcf file
        vcf_type (str): gatk | delly specifying vcf type.
    """
    vcf_name = vcf_file.split('/')[-1].replace(".vcf","")
    # Setup bulk upload variables
    variant_count = 0
    bulk_variants = db.variants.initialize_unordered_bulk_op()

    if db.vcfs.find({'name':vcf_name}).limit(1).count() > 0:
        sys.exit("Error: Duplicate vcf name.")

    # Setup vcf metadata dictonary, upload to vcfs collection
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

                # Parse header lines
                if line.startswith('#'):
                    header_line_metadata = vcf_header(line)
                    deep_update(vcf_metadata, header_line_metadata)

                # Parse variant lines
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
                            variant_count += len(variants)

                    elif vcf_type == 'delly':
                        variant, variant_samples = delly_line(line, vcf_metadata)
                        variant_id = '{}-{}-{}-{}-{}-{}'.format(variant['chr'], variant['pos'], variant['ref'], variant['alt'], variant['CHR2'], variant['END'])
                        bulk_variants.find({'_id':variant_id}).upsert().update({
                            '$push': {'samples': {'$each': variant_samples}},
                            '$set': variant,
                            }
                        )
                        variant_count += 1

                    #Upload variants in bulk
                    if variant_count >= 500:
                        bulk_variants.execute()
                        bulk_variants = db.variants.initialize_unordered_bulk_op()
                        variant_count = 0
        # insert remaining variants and insert vcf metadata to vcfs collection
        bulk_variants.execute()
        db.vcfs.insert_one(vcf_metadata)

def vcf_header(line):
    """
    Parse vcf header line

    Args:
        line (str): vcf header line
    Returns:
        dict: metadata dictonary
    """
    line_metadata = {}
    if line.startswith('##FILTER') or line.startswith('##ALT'):
        data = re.search('(?:##)(\w+)(?:=<ID=)(\w+)(?:,Description=")(.+)(?:">)', line).groups()
        line_metadata[data[0]] = {data[1] : data[2]}

    elif line.startswith('##INFO') or line.startswith('##FORMAT'):
        try:
          data = re.search('(?:##)(\w+)(?:=<ID=)(\S+)(?:,Number=)(.+)(?:,Type=)(\w+)(?:,Description=")(.+)(?:">)',line).groups()
          line_metadata[data[0]] = {
              data[1].replace(".", "-") : {
                      'number': data[2],
                      'type': data[3],
                      'description': data[4]
                }
            }
        except AttributeError:
          print "Error: Cannot parse this INFO line correctly: \n" + line
          print "\nProgram is now closed."
          sys.exit()

    elif line.startswith('##contig'):
        try:
          data = re.search('(?:##contig=<ID=)(\w+)(?:,length=)(.+)(?:>)', line).groups()
          line_metadata['contig'] = {
              data[0] : {
              'length' : data[1]
                }
            }
        except AttributeError:
          print "Error: Cannot parse this contig line correctly: \n" + line
          print "\nProgram is now closed."
          sys.exit()

    elif line.startswith('#CHROM'):
        line_metadata['samples'] = line.split()[9:]

    elif line.startswith('##GATKCommandLine.'):
        try:
            # gatk_commandline = re.search('(?:##)([GATKCommandLine\S]+)', line).groups()
            # gatk_id = re.search('(?:=<ID=)(.+)', line).groups()
            # gatk_version = re.search('(?:,Version=)(.+)', line).groups()
            # gatk_date = re.search('(?:,Date=)(.+)', line).groups()
            # gatk_epoch = re.search('(?:,Epoch=)(.+)', line).groups()
            # gatk_commandlineoptions = re.search('(?:,CommandLineOptions=)(.+)(?:">)', line).groups()
            data = re.search('(?:##)([GATKCommandLine\S]+)(?:=<ID=)(.+)(?:,Version=)(.+)(?:,Date=)(.+)(?:,Epoch=)(.+)(?:,CommandLineOptions=)(.+)(?:">)',line).groups()
            line_metadata["GATKCommandLine"] = {
                data[1] : {
                'version': data[2],
                'date': data[3],
                'epoch': data[4],
                'commandlineoptions': data[5]
                }
            }
        except AttributeError:
            #print "Error: Cannot parse this GATKCommand line correctly: \n" + line
            #print "\nProgram is now closed."
            return line_metadata

    else:
        try:
          data = re.search('(?:##)(\S+)(?:=)(.+)',line).groups()
          line_metadata[data[0]] = data[1]
        except AttributeError:
          print "Error: Cannot parse this GATKCommand line correctly: \n" + line
          print "\nProgram is now closed."
          sys.exit()

    return line_metadata

def gatk_line(line, vcf_metadata):
    """
    Parse gatk variant line.
    VCF lines containing multiple alternative alleles are splitted by alternative allele and
    get a minimal (left aligned) representation. Sample information (e.g. genotype)
    is added to seperate list of sample dictionaries to be able to update exisiting variants.

    Args:
        line (str): gatk vcf variant line
        vcf_metadata (dict): metadata dictonary containing vcf header data
    Returns:
        list: variants, list of variant dictionaries.
        list: variants_samples, list of variant samples lists.
    """
    # Setup general variables

    fields = line.split('\t')
    #external_ids = fields[2].split(',') # Split per alternative allele?
    gt_format = fields[8].split(':')
    info_field = fields[7].split(";")
    variants = []
    variants_samples = []

    # Different variant per alt allele
    # 1/2 variants are splitted into two variants with genotype: 1/-
    # https://github.com/samtools/hts-specs/issues/77
    alt_alleles = fields[4].split(',')
    info_dict = {}
    """
    Parses INFO-field specific for SnpEff ANN field, CADD field and remaining (other) fields.
    """
    for alt in range(0, len(alt_alleles)):
        # Create INFO-dict for each alt allele
        info_dict[alt_alleles[alt]] = {}
        for info_line in info_field:
            try:
                # SnpEff ANN field
                if info_line.split("=")[0] == "ANN":
                    if vcf_metadata["INFO"]["ANN"]["description"] not in info_dict:
                        ann_header = vcf_metadata["INFO"]["ANN"]["description"]
                        ann_header = ann_header.split(" | ")
                    ann_info = ""
                    ann_info += info_line.split("=")[1]

                    for ann_line in ann_info.split(","):
                        alts = ann_line.split("|")
                        annFieldDict(ann_info, ann_header, info_dict)

                # CADD field
                elif info_line.split("=")[0].startswith("CADD"):
                    if "CADD" not in info_dict[alt_alleles[alt]].keys():
                        info_dict[alt_alleles[alt]]["CADD"] = {}
                    keys, values = createKeyVals(info_line, alt)

                    info_dict[alt_alleles[alt]]["CADD"][keys.replace(".", "-")] = values
                    # Convert datatype based on header (meta data) information
                    info_dict[alt_alleles[alt]]["CADD"] = convert_data(info_dict[alt_alleles[alt]]["CADD"], vcf_metadata['INFO'])

                # 'Other' field
                else:
                    keys, values = createKeyVals(info_line, alt)
                    info_dict[alt_alleles[alt]][keys] = values
            except IndexError:
                # solve indexerror
                pass

    for alt_index, alt_allele in enumerate(alt_alleles):
        pos, ref, alt = get_minimal_representation(fields[1], fields[3], alt_allele)

        variant = {
            'chr': fields[0],
            'pos' : pos,
            'ref' : ref,
            'alt' : alt,
            'info' : info_dict[alt_allele]
        }
        variants.append(variant)

        # Parse samples
        variant_samples = []
        for sample_index, sample in enumerate(vcf_metadata['samples']):
            sample_gt_data = fields[9+sample_index].split(':')
            # Skip variant if no or reference call.
            if(sample_gt_data[gt_format.index('GT')] != './.' and sample_gt_data[gt_format.index('GT')] != '0/0'):
                sample_gt_data = adjust_genotype(sample_gt_data, gt_format, alt_index)
                # Skip reference call after splitting alternative alleles.
                if sample_gt_data[0] != "0/-":
                    sample_var = {}
                    sample_var['genotype'] = convert_data(dict(zip(gt_format, sample_gt_data)), vcf_metadata['FORMAT'])
                    sample_var['sample'] = sample
                    sample_var['vcf_id'] = vcf_metadata['_id']

                    # Set filter field
                    if fields[6] == "PASS" or fields[6] ==".":
                        pass
                    else:
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
    """
    Convert vcf data using metadata dictonary

    Args:
        data (dict): dictonary with str values
        metadata (dict): metadata dictonary containing vcf header data needed to convert values in data dict
    Returns:
        data (dict): converted data dictonary
    """
    for id in data:
        if data[id] != ".":
            if ',' in data[id]:
                data[id] = data[id].split(',')

            if type(data[id]) is list:
                if metadata[id]['type']  == "Integer":
                    data[id] = [int(item) if item != 'NA' else 'NA' for item in data[id]]
                elif metadata[id]['type']  == "Float":
                    data[id] = [float(item) if item != 'NA' else 'NA' for item in data[id]]
            else:
                if metadata[id]['type']  == "Integer":
                    data[id] = int(data[id])
                elif metadata[id]['type']  == "Float":
                    data[id] = float(data[id])
    return data

def adjust_genotype(gt_data, gt_format, alt_index, allele_symbol = '-'):
    """
    Adjust genotype fields by alternative allele index

    Args:
        gt_data (list): sample genotype data as list
        gt_format (list): vcf gt format column as list
        alt_index (int): Alternative allele index
        allele_symbol (str): replacment genotype symbol for overlapping variants
    Returns:
        gt_data (list): Adjusted gt data

    """
    for gt_i, gt_field in enumerate(gt_data):
        gt_key = gt_format[gt_i]
        # For now only parse GT and AD also change PL?
        if gt_key == 'GT':
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

def createKeyVals(info_line, alt):
    """
    If a value consists of multiple transcripts that have identical values, only one will be stored.
    Makes a keylist for all values before "=" & makes a valuelist for all values after "="
    and returns these lists.
    """
    cadd_vals = info_line.split("=")[1]
    if "," in cadd_vals:
        multi_cadd = cadd_vals.split(",")
        values = multi_cadd[alt].split("|")
    else:
        values = cadd_vals.split("|")
    keys = info_line.split("=")[0]
    return keys, values

def annFieldDict(ann_info, ann_header, info_dict):
    """
    Create a ANN dictionary based on each transcript ID (FeatureID).
    Will not store key/value pair if the value is empty.
    """
    # Replace all dots with an underscore (bulkwrite error solve)
    ann_header = [i.replace(".", "_") for i in ann_header]
    ann_transcript = [i.replace(".", "_") for i in ann_info.split(",")]

    for ann_line in ann_transcript:
        ann_values = ann_line.split("|")

        # Create ANN-dict that parses each ANN-line.
        # Use deep_update to update the info dictionary.
        for line_pos in range(1, len(ann_header)):
            if ann_values[line_pos]:
                ann_dict = {ann_values[0]: {'ANN' : {ann_values[1]: {ann_values[6]: {ann_header[line_pos]: ann_values[line_pos]}}}}}
                deep_update(info_dict, ann_dict)
