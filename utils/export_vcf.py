
import re
import vcf as py_vcf
import sys
import collections

from StringIO import StringIO

from . import db
from . import query

# Create template vcf
vcf = py_vcf.Reader(StringIO("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT"))

def export( filter_query=False ):
    
    # Convert query
    if "SAMPLE=" in filter_query:
        filter_query = filter_query.replace("SAMPLE=", "SAMPLE!=")
    else:
        sys.exit('Bad filter query')
    
    # Create mongo query
    if filter_query:
        sample_match_query = re.match(r"^SAMPLE(=|\!=|\?=)\[?(\S+)\]?", filter_query)        
        if sample_match_query:
            my_sample_query, my_sample_query_2 = query.create_sample_query( filter_query )
        
    
    query_aggregate = [ 
        {
            '$unwind': '$samples'
        },
        {
            '$match': my_sample_query
        },
    ]
    
    # Get variants from variants document
    variant_aggregate = list(db.variants.aggregate(query_aggregate))
    
    # Rewrite query to get vcf info from vcfs document
    query_aggregate[1]['$match']['samples'] = query_aggregate[1]['$match']['samples.sample']
    del query_aggregate[1]['$match']['samples.sample']

    # Get vcf info from vcfs document
    vcfs_aggregate = list(db.vcfs.aggregate(query_aggregate))
    
    # Loop through vcfs to parse the headers
    for vcf2 in vcfs_aggregate:
        vcf.metadata = vcf2['metadata']
        parse_contig_header( vcf2['contig'] )
        parse_info_header( vcf2['info'] )
        parse_format_header ( vcf2['format'] )
        parse_filter_header( vcf2['filter'] )
        parse_alt_header( vcf2['alt'] )
    
    # Open vcf Writer
    vcf_writer = py_vcf.Writer(sys.stdout, vcf)
    
    for variant in variant_aggregate: 
        record = parse_variant( variant )
        vcf_writer.write_record( record )
        
def parse_variant( variant ):
    # Set variant variables    
    chrom = variant['chr']
    pos = variant['pos']
    id = variant['samples']['id']
    ref = variant['ref']
    qual = variant['samples']['qual']
    
    # Set ALT variable
    if not '<' in variant['alt']:
        if variant['samples']['info']['SVTYPE'] != 'BND':
            alt = py_vcf.model._Substitution( variant['alt'] )
        else:
            alt = py_vcf.model._Breakend(variant['chr2'],variant['end'],variant['orientation'],variant['remoteOrientation'],variant['alt'],True)
    else:
        alt = py_vcf.model._SV(variant['alt'][1:-1])
        
    # Set FILTER variable
    if 'filter' in variant['samples']:
        filter = variant['samples']['filter']
    else:
        filter = ['PASS']
    
    # Set INFO variable
    info = variant['samples']['info']
    if 'POS_RANGE' in info:
        del info['POS_RANGE']
    if 'END_RANGE' in info:
        del info['END_RANGE']

    # Set FORMAT variable
    format_list = sorted( variant['samples']['genotype'].keys() )
    format_list.remove('GT')
    format_list.insert(0,'GT')        
    format = ':'.join( format_list )
    
    # Set SAMPLES variable
    call = py_vcf.model._Call('site',variant['samples']['sample'], collections.namedtuple('CallData', format_list)(**variant['samples']['genotype']) )
    samples = [ call ]
    samples_indexes = [0]

    record = py_vcf.model._Record( chrom, pos, id, ref, [alt], qual, filter, info, format, samples_indexes, samples )
    return ( record )        

def parse_contig_header( contig_dict ):
    for id, length in sorted(contig_dict.iteritems() ):
        contig = py_vcf.parser._Contig(id, length)
        vcf.contigs[ contig[0] ] = contig
        
def parse_info_header( info_dict ):
    for id, value in sorted(info_dict.iteritems() ):
        info = py_vcf.parser._Info(id, value['num'], value['type'], value['desc'], value['source'], value['version'])
        vcf.infos[ info[0] ] = info

def parse_format_header( format_dict ):
    for id, value in sorted(format_dict.iteritems() ):
        format = py_vcf.parser._Format(id, value['num'], value['type'], value['desc'])
        vcf.formats[ format[0] ] = format

def parse_filter_header( filter_dict ):
    for id, desc in sorted(filter_dict.iteritems() ):
        filter = py_vcf.parser._Filter(id, desc)
        vcf.filters[ filter[0] ] = filter

def parse_alt_header( alt_dict ):
    for id, desc in sorted(alt_dict.iteritems() ):
        alt = py_vcf.parser._Alt(id, desc)
        vcf.alts[ alt[0] ] = alt
