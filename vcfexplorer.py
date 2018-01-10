#!/usr/bin/env python

"""
    vcfexplorer.py

    VCF Explorer management application.
"""

import argparse

from vcfexplorer import app
import utils

def runserver(args):
    app.run(host=args.hostname, port=args.port)

def upload_vcf(args):
    utils.parse_vcf.upload_vcf(args.vcf_file)

def filter_vcf(args):
    utils.filter_vcf.filter_sv_vcf(args.vcf_file, args.flank, args.name, args.query, args.ori)
    
def resetdb(args):
    utils.database.resetdb()

def create_indexes(args):
    utils.database.create_indexes()

#def query_database(args):
    #print "TEST"
    #print args.query_line
    #print utils.query.execute(args.query_line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # VCF file arguments
    import_vcf = argparse.ArgumentParser(add_help=False)
    import_vcf.add_argument('vcf_file', help='path/to/file.vcf')

    # VCF filter arguments
    filter_vcf_args = argparse.ArgumentParser(add_help=False)
    filter_vcf_args.add_argument('vcf_file', help='path/to/file.vcf')
    filter_vcf_args.add_argument('-f','--flank', default=10, type=int, help='Flank to increase filter search space [10]')
    filter_vcf_args.add_argument('-n','--name', default='DB', type=str, help='Filter name [DB]')
    filter_vcf_args.add_argument('-q','--query', default='', type=str, help='Filter query')
    filter_vcf_args.add_argument('-o','--ori', action='store_true', help='Including orientation')

    # Server arguments
    server = argparse.ArgumentParser(add_help=False)
    server.add_argument('-host','--hostname', default='localhost', help='The hostname to listen on.')
    server.add_argument('-p','--port', default=5000, type=int, help='The port of the webserver.')

    # Query arguments
    query_line = argparse.ArgumentParser(add_help=False)
    query_line.add_argument('query_line', help='Query the database')

    sp = parser.add_subparsers()
    sp_runserver = sp.add_parser('runserver', parents=[server], help='Run flask development server')
    sp_import_vcf = sp.add_parser('import', parents=[import_vcf] ,help='Upload a vcf file to the database')
    sp_filter_vcf = sp.add_parser('filter', parents=[filter_vcf_args] ,help='Filter a vcf file using the database')
    sp_resetdb = sp.add_parser('resetdb', help='Resetdb mongodb')
    sp_create_indexes = sp.add_parser('createindex', help='Create indexes')
    #sp_query = sp.add_parser('query', parents=[query_line], help='Query database')

    sp_runserver.set_defaults(func=runserver)
    sp_import_vcf.set_defaults(func=upload_vcf)
    sp_filter_vcf.set_defaults(func=filter_vcf)
    sp_resetdb.set_defaults(func=resetdb)
    sp_create_indexes.set_defaults(func=create_indexes)
    #sp_query.set_defaults(func=query_database)

    args = parser.parse_args()
    args.func(args)
