import re
import pymongo
import query as qu
 
connection = pymongo.MongoClient("mongodb://localhost")
db = connection.sv_database
variants = db.variants
vcfs = db.vcfs
samples = db.samples

def execute(q):
  query = qu.create(q)
  query = eval(query)
  hits = db.variants.find(query)
  sampleNames = dict()
  variants = dict()
  for hit in hits:
    variant_list = [hit['CHR'],str(hit['POS']),".",hit['REF'],hit['ALT'],str(hit['QUAL']),"."] 
    info_list = ["SVTYPE="+hit['VARIANT_INFO']['SVTYPE'],"CHR2="+hit['VARIANT_INFO']['CHR2'],"END="+str(hit['VARIANT_INFO']['END']),"CT="+hit['VARIANT_INFO']['CT']]
    format_list = ["GT","GL","GQ","FT","RCL","RC","RCR","CN","DR","DV","RR","RV"]    
    for sample in hit['SAMPLES']:
      sampleNames[sample['NAME']] = 1
      sample_format_list = list()
      for f in format_list:
	sample_format_list.append(str(sample['FORMAT'][f]))
      
      if "\t".join(variant_list) in variants:
	if ";".join(info_list) in variants["\t".join(variant_list)]:
	  if ":".join(format_list) in variants["\t".join(variant_list)][";".join(info_list)]:
	    variants["\t".join(variant_list)][";".join(info_list)][":".join(format_list)][sample['NAME']] = ":".join(sample_format_list)
	  else:
	    variants["\t".join(variant_list)][";".join(info_list)][":".join(format_list)] = dict()
	else:
	  variants["\t".join(variant_list)][";".join(info_list)] = dict()
      else:
	variants["\t".join(variant_list)] = dict()
  print "##FILTER=<ID=DatabaseQuery,Description=\""+q+"\">"
  print "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(sampleNames.keys())
  
  for var in variants:
    for inf in variants[var]:
      for form in variants[var][inf]:
	print var + "\t" + inf + "\t" + form,
	for sample in sampleNames:
	  if sample in variants[var][inf][form]:
	    print "\t" + variants[var][inf][form][sample],
	  else:
	    print "\t" + "./.",
	print ""
  #print sampleNames