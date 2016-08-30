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

def loadvcf(args):
    utils.parse_vcf.upload_vcf(args.vcf_file, args.vcf_template)

def resetdb(args):
    utils.database.resetdb()

def create_indexes(args):
    utils.database.create_indexes()

def query_database(args):
    print "TEST"
    print args.query_line
    #utils.query.help()
    print utils.query.execute(args.query_line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # VCF file arguments
    vcf_file = argparse.ArgumentParser(add_help=False)
    #vcf_file.add_argument('vcf_type', help='VCF type', choices=['gatk', 'delly'])
    vcf_file.add_argument('vcf_template', help='path/to/vcf_type_template.json')
    vcf_file.add_argument('vcf_file', help='path/to/file.vcf')

    # Server arguments
    server_port = argparse.ArgumentParser(add_help=False)
    server_port.add_argument('-p','--port', default=5000, type=int, help='The port of the webserver.')
    server_host =argparse.ArgumentParser(add_help=False)
    server_port.add_argument('-host','--hostname', default='localhost', help='The hostname to listen on.')

    # Query arguments
    query_line = argparse.ArgumentParser(add_help=False)
    query_line.add_argument('query_line', help='Query the database')

    sp = parser.add_subparsers()
    sp_runserver = sp.add_parser('runserver', parents=[server_port,server_host], help='Run flask development server')
    sp_vcf = sp.add_parser('vcf', parents=[vcf_file] ,help='Upload a vcf file to the database')
    sp_resetdb = sp.add_parser('resetdb', help='Resetdb mongodb')
    sp_create_indexes = sp.add_parser('createindex', help='Create indexes')
    sp_query = sp.add_parser('query', parents=[query_line], help='Query database')

    sp_runserver.set_defaults(func=runserver)
    sp_vcf.set_defaults(func=loadvcf)
    sp_resetdb.set_defaults(func=resetdb)
    sp_create_indexes.set_defaults(func=create_indexes)
    sp_query.set_defaults(func=query_database)

    args = parser.parse_args()
    args.func(args)
