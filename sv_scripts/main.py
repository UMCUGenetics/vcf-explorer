import sys
import argparse
import pymongo
import re
import warnings

import query
import filter
import get

parser = argparse.ArgumentParser(description='Process VCF file',add_help=False)
subparsers = parser.add_subparsers(title="MODE")
parser_options_group = parser.add_argument_group(title="Options")
parser_options_group.add_argument('-h','--help',action='help',help="")

filter_parser = subparsers.add_parser('filter',help='Filter a VCF file',add_help=False)
filter_required_group = filter_parser.add_argument_group(title='Required')
filter_required_group.add_argument('-v','--vcf',type=str, required=True, help='Input VCF file')
filter_options_group = filter_parser.add_argument_group(title='Options')
filter_options_group.add_argument('-h','--help',action='help',help="")
filter_options_group.add_argument('-d','--distance',type=int,help="Maximum flank distance (DEFAULT: 500)", default=500)
filter_options_group.add_argument('-p','--percentage',type=int,help="Percentage flank distance (DEFAULT: 5)",default=5)
filter_options_group.add_argument('-q','--query',type=str,help="Filter query")

query_parser = subparsers.add_parser('query',help='Show query help',add_help=False)

get_parser = subparsers.add_parser('get',help='Get data from the database', add_help=False)
get_required_group = get_parser.add_argument_group(title='Required')
get_required_group.add_argument('-q','--query',type=str, required=True, help='Query')
get_options_group = get_parser.add_argument_group(title='Options')
get_options_group.add_argument('-h','--help',action='help',help="")

args = parser.parse_args()

if sys.argv[1] == "filter":
  q = ""
  #if args.query:
    #q = query.create(args.query)
  filter.delly(args.vcf, args.distance, args.percentage,args.query)
elif sys.argv[1] == "query":
  query.help()
elif sys.argv[1] == "get":
  #q = query.create(args.query)
  get.execute(args.query)
