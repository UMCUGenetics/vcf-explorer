"""
    query.py

    Utility functions to query vcf explorer from the command line.
    Needs refactoring -> delly hardcoded code.
"""
import re
import pymongo

from . import connection, db

def create_sample_query( query_command ):
    match = re.match(r"^SAMPLE(=|\!=|\?=)\[?(.+)\]?",query_command)
    
    query = {}  
    query_2 = {}
    if match:
        sample_list = match.group(2).split(',')
        sample_list[-1] = sample_list[-1].replace("]","")
    
    # Create must query
    if match.group(1) == "=":
        
        ## Variant may not be present in all other samples in the database
        query['samples'] = { '$elemMatch': { 'sample': { '$nin': sample_list} } }
    
        ## Check if the Variant is be present in the given sample(s), otherwise it get the filter NotPresent
        query_2['samples.sample'] = { '$in': sample_list }
        
    # Create may query
    elif match.group(1) == "?=":
        ## Variant may only be present in the given sample(s)
        query['samples'] = { '$elemMatch': { 'sample': { '$nin': sample_list} } }
    
    # Create against query
    elif match.group(1) == "!=":
        ## Filter variant only when its present in the given sample(s)
        query['samples.sample'] = { '$in': sample_list }

    return query, query_2
