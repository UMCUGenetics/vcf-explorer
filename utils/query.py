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
	if match:
		sample_list = match.group(2).split(',')
	
	# Create must query
	if match.group(1) == "=":
		query['$or'] = [ 
			{ 'samples': { '$size': len(sample_list) } }, 
			{ 'samples.sample': { '$not': { '$all': sample_list } }}
		]
		query['$and'] = [
			{ 'samples': { '$size': len(sample_list) } }, 
			{ 'samples.sample': { '$all': sample_list } }
		]
		
	# Create may query
	elif match.group(1) == "?=":
		query['samples'] = { '$elemMatch': { 'sample': { '$nin': sample_list} } }
	
	# Create against query
	elif match.group(1) == "!=":
		query['samples.sample'] = { '$in': sample_list }

	return query









#numerics = {
  #"POS": "Integer",
  #"END": "Integer",
  #"INSLEN": "Integer",
  #"PE": "Integer",
  #"MAPQ": "Integer",
  #"SR": "Integer",
  #"SRQ": "Float",
  #"GQ": "Integer",
  #"RC": "Integer",
  #"RCL": "Integer",
  #"RCR": "Integer",
  #"CN": "Integer",
  #"DR": "Integer",
  #"DV": "Integer",
  #"RR": "Integer",
  #"RV": "Integer"
 #}

#fields = {
  #"chr": "'chr'",
  #"pos": "'pos'",
  #"CHR2": "'VARIANT_INFO.CHR2'",
  #"END": "'VARIANT_INFO.END'",
  #"SVTYPE": "'VARIANT_INFO.SVTYPE'",
  #"CT": "'VARIANT_INFO.CT'",
  #"SAMPLE": "'SAMPLES.NAME'",
  #"FILTER": "'SAMPLES.FILTER'",
  #"GT": "'SAMPLES.FORMAT.GT'",
  #"GL": "'SAMPLES.FORMAT.GL'",
  #"GQ": "'SAMPLES.FORMAT.GQ'",
  #"FT": "'SAMPLES.FORMAT.FT'",
  #"RCL": "'SAMPLES.FORMAT.RCL'",
  #"RC": "'SAMPLES.FORMAT.RC'",
  #"RCR": "'SAMPLES.FORMAT.RCR'",
  #"CN": "'SAMPLES.FORMAT.CN'",
  #"DR": "'SAMPLES.FORMAT.DR'",
  #"DV": "'SAMPLES.FORMAT.DV'",
  #"RR": "'SAMPLES.FORMAT.RR'",
  #"RV": "'SAMPLES.FORMAT.RV'",
  #"PRECISE": "'SAMPLES.INFO.PRECISE'",
  #"CIEND": "'SAMPLES.INFO.CIEND'",
  #"CIPOS": "'SAMPLES.INFO.CIPOS'",
  #"INSLEN": "'SAMPLES.INFO.INSLEN'",
  #"PE": "'SAMPLES.INFO.PE'",
  #"MAPQ": "'SAMPLES.INFO.MAPQ'",
  #"SR": "'SAMPLES.INFO.SR'",
  #"SRQ": "'SAMPLES.INFO.SRQ'"
 #}

#operators = {
    #"=": '$eq',
    #"!=": '$ne',
    #">": '$gt',
    #">=": '$gte',
    #"<": '$lt',
    #"<=": '$lte',
    #"=[": '$in',
    #"!=[": '$nin',
    #"=~": '$regex'
 #}

#logical_operators = {
    #"&": '$and',
    #"|": '$or'
#}

#logical_operators_list = []
#fields_list = []
#operators_list = []

#for o in sorted(operators, key=len, reverse=True):
    #operators_list.append(re.escape(o))
#op_regex = "(" + "|".join(operators_list) + ")"

#for l in sorted(logical_operators, key=len, reverse=True):
    #logical_operators_list.append(re.escape(l))
#lop_regex = "(" + "|".join(logical_operators_list) + ")"

#for f in sorted(fields, key=len, reverse=True):
    #fields_list.append(re.escape(f))
#field_regex = "(" + "|".join(fields_list) + ")"

#def help():
    #print "\nFIELDS"
    #print "-------------------------------------------------------------------------"
    #print "|        Field        |        DB_field        |          Type          |"
    #print "-------------------------------------------------------------------------"

    #for f in sorted(fields):
        #t = "String"
        #if f in numerics:
            #t = numerics[f]
        #print "| "+f+(" "*(20-len(f)))+"| "+fields[f]+(" "*(23-len(fields[f])))+"| "+t+(" "*(23-len(t)))+"|"
    #print "-------------------------------------------------------------------------"

    #print "\nOPERATORS"
    #print "------------------------------------------------"
    #print "|      Operator       |      DB_operator       |"
    #print "------------------------------------------------"
    #for o in sorted(operators):
        #print "| "+o+(" "*(20-len(o)))+"| "+operators[o]+(" "*(23-len(operators[o])))+"|"
    #print "------------------------------------------------"

    #print "\nLOGICAL OPERATORS"
    #print "------------------------------------------------"
    #print "|  Logical Operator   |   DB_logical_operator  |"
    #print "------------------------------------------------"
    #for l in sorted(logical_operators):
        #print "| "+l+(" "*(20-len(l)))+"| "+logical_operators[l]+(" "*(23-len(logical_operators[l])))+"|"
    #print "------------------------------------------------"

    #print "\nEXAMPLE"
    #print "-q \"CHR='1' & (SVTYPE='DEL' | SVTYPE='DUP') & GT=['1/1','0/1'] & MAPQ>10\"\n"
    #return 0;

#def create(args):
    #query = parse(args)
    #return query

#def convert(arg):
    #arg = re.sub("^\(","",arg)
    #arg = re.sub("\)$","",arg)
    #match = re.match(r""+field_regex+op_regex+"(.+)"+"\s+"+lop_regex+"\s+"+field_regex+op_regex+"(.+)",arg)
    #q = ""

    #if match:
        #if operators[match.group(2)] == "$in" or operators[match.group(2)] == "$nin":
            #q = " { '" + logical_operators[match.group(4)] + "': [ { " + fields[match.group(1)] + ": { '" + operators[match.group(2)] + "': [" + match.group(3) + " } }, "
        #else:
            #q = " { '" + logical_operators[match.group(4)] + "': [ { " + fields[match.group(1)] + ": { '" + operators[match.group(2)] + "': " + match.group(3) + " } }, "
        #if operators[match.group(6)] == "$in" or operators[match.group(6)] == "$nin":
            #q = q + "{ " + fields[match.group(5)] + ": { '" + operators[match.group(6)] + "': [" + match.group(7) + " } } ] }"
        #else:
            #q = q + "{ " + fields[match.group(5)] + ": { '" + operators[match.group(6)] + "': " + match.group(7) + " } } ] }"

    #else:
        #match2 = re.match(r""+field_regex+op_regex+"(.+)",arg)
        #if operators[match2.group(2)] == "$in" or operators[match2.group(2)] == "$nin":
            #q = " { " + fields[match2.group(1)] + ": { '" + operators[match2.group(2)] + "': [" + match2.group(3) + " } }"
        #else:
            #q = " { " + fields[match2.group(1)] + ": { '" + operators[match2.group(2)] + "': " + match2.group(3) + " } }"
    #return q

#def parse(arg):
    #match = re.match(r"^\((([^\(])*|.*)\)\s+"+lop_regex+"\s+(.+)",arg)
    #q = ""
    #q1 = ""
    #q2 = ""

    #if match:
        #if len(re.findall(r""+lop_regex,match.group(1))) > 1:
            #q1 = parse(match.group(1))
        #elif len(re.findall(r""+lop_regex,match.group(1))) == 1:
            #q1 = convert(match.group(1))
        #if len(re.findall(r""+lop_regex,match.group(4))) > 1:
            #q2 = parse(match.group(4))
        #elif len(re.findall(r""+lop_regex,match.group(4))) == 1:
            #q2 = convert(match.group(4))
    #else:
        #match = re.match(r"^(([^\(])*?|.*?)\s+"+lop_regex+"\s+(.+)",arg)
        #if match:
            #if len(re.findall(r""+lop_regex,match.group(1))) > 1:
                #q1 = parse(match.group(1))
            #elif len(re.findall(r""+lop_regex,match.group(1))) == 1:
                #q1 = convert(match.group(1))
            #if len(re.findall(r""+lop_regex,match.group(4))) > 1:
                #q2 = parse(match.group(4))
            #elif len(re.findall(r""+lop_regex,match.group(4))) == 1:
                #q2 = convert(match.group(4))
            #if len(re.findall(r""+lop_regex,match.group(4))) == 0 and len(re.findall(r""+lop_regex,match.group(1))) == 0:
                #q = convert(arg)
        #else:
            #q = convert(arg)

    #if q1 and q2:
        #q = " { '" + logical_operators[match.group(3)] + "' : [ " + q1 + "," + q2 + " ] }"

    #elif q1:
        #match2 = re.match(r""+field_regex+op_regex+"(.+)",match.group(4))
        #if match2:
            #if operators[match2.group(2)] == "$in" or operators[match2.group(2)] == "$nin":
                #q = " { '" + logical_operators[match.group(3)] + "': [ " + q1 + ", { " + fields[match2.group(1)] + ": { '" + operators[match2.group(2)] + "': [" + match2.group(3) + " } } ] }"
            #else:
                #q = " { '" + logical_operators[match.group(3)] + "': [ " + q1 + ", { " + fields[match2.group(1)] + ": { '" + operators[match2.group(2)] + "': " + match2.group(3) + " } } ] }"
    #elif q2:
        #match1 = re.match(r""+field_regex+op_regex+"(.+)",match.group(1))
        #if match1:
            #if operators[match1.group(2)] == "$in" or operators[match1.group(2)] == "$nin":
                #q = " { '" + logical_operators[match.group(3)] + "': [ { " + fields[match1.group(1)] + ": { '" + operators[match1.group(2)] + "': [" + match1.group(3) + " } } , " + q2 + " ] }"
            #else:
                #q = " { '" + logical_operators[match.group(3)] + "': [ { " + fields[match1.group(1)] + ": { '" + operators[match1.group(2)] + "': " + match1.group(3) + " } } , " + q2 + " ] }"
    #return q

#def execute(q):
    #query = create(q)
    #query = eval(query)
    #hits = db.variants.find(query)
    #sampleNames = dict()
    #variants = dict()
    #for hit in hits:
        #variant_list = [hit['chr'],str(hit['pos']),".",hit['ref'],hit['alt'],".","."]#,str(hit['QUAL']),"."]
        #info_list = ["SVTYPE="+hit['SVTYPE'],"CHR2="+hit['CHR2'],"END="+str(hit['END']),"CT="+hit['CT']]
        #format_list = ["GT","GL","GQ","FT","RCL","RC","RCR","CN","DR","DV","RR","RV"]
        #for sample in hit['samples']:
            #sampleNames[sample['sample']] = 1
            #sample_format_list = list()

            #for f in format_list:
                #sample_format_list.append(str(sample['genotype'][f]))
                #if "\t".join(variant_list) in variants:
                    #if ";".join(info_list) in variants["\t".join(variant_list)]:
                        #if ":".join(format_list) in variants["\t".join(variant_list)][";".join(info_list)]:
                            #variants["\t".join(variant_list)][";".join(info_list)][":".join(format_list)][sample['sample']] = ":".join(sample_format_list)
                        #else:
                            #variants["\t".join(variant_list)][";".join(info_list)][":".join(format_list)] = dict()
                    #else:
                        #variants["\t".join(variant_list)][";".join(info_list)] = dict()
                #else:
                    #variants["\t".join(variant_list)] = dict()

    #print "##FILTER=<ID=DatabaseQuery,Description=\""+q+"\">"
    #print "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(sampleNames.keys())

    #for var in variants:
        #for inf in variants[var]:
            #for form in variants[var][inf]:
                #print var + "\t" + inf + "\t" + form,

                #for sample in sampleNames:
                    #if sample in variants[var][inf][form]:
                        #print "\t" + variants[var][inf][form][sample],
                    #else:
                        #print "\t" + "./.",
                #print ""
