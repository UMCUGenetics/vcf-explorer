import re
import pymongo
import warnings
import vcf
import json
import query as qu

connection = pymongo.MongoClient("mongodb://localhost")
db = connection.sv_database
variants = db.variants
vcfs = db.vcfs
samples = db.samples

def delly(vcf_file, max_flank, perc, q):
  filter_print = False
  info_db_print = False
  with open(vcf_file, 'r') as f:
    for line in f:
      line = line.strip('\n')
      if line.startswith('##'):
	if line.startswith('##INFO') and not filter_print:
	  print "##FILTER=<ID=DB,Description=\"SV found in database.\">"
	  filter_print = True
	print line
	continue
      elif line.startswith('#'):
	print "##FILTER=<ID=Distance,Description=\"Maximum flank distance, used: "+str(max_flank)+"\">"
	print "##FILTER=<ID=Percentage,Description=\"Percentage flank distance, used: "+str(perc)+"\">"
	if q:
	  print "##FILTER=<ID=DatabaseQuery,Description=\""+q+"\">"
	  
	samples = line.split()[9:]
	print line
	continue
      
      fields = line.split('\t')

      gt_format = fields[8].split(':')
      info_fields = dict(item.split("=") for item in fields[7].split(";")[1:])            
      info_fields["PRECISE"] = fields[7].split(";")[0]
      
      flank = max_flank
      if (info_fields['SVTYPE'] != "TRA"):
	size = (int(info_fields['END'])-int(fields[1]))
	flank = size/100*perc
      if (flank > max_flank):
	flank = max_flank
      
      chrom = fields[0].upper()
      chrom = re.sub("^chr","",chrom,flags=re.I)
      start1 = int(fields[1])-flank
      end1 = int(fields[1])+flank
      chrom2 = info_fields['CHR2']
      chrom2 = re.sub("^chr","",chrom2,flags=re.I)
      start2 = int(info_fields['END'])-flank
      end2 = int(info_fields['END'])+flank
      svtype = info_fields['SVTYPE']
      ct = info_fields['CT']
            
      query = {'CHR':chrom,'POS': {'$gte':start1,'$lte': end1},
      'VARIANT_INFO.CHR2':chrom2, 'VARIANT_INFO.END':{'$gte':start2,'$lte':end2},
      'VARIANT_INFO.SVTYPE':svtype,'VARIANT_INFO.CT':ct }
      
      if (svtype == "TRA"):
	ct2 = ct
	if (ct == "3to5"):
	  ct2 = "5to3"
	elif (ct == "5to3"):
	  ct2 = "3to5"
	query = { '$or' : [
	  { 'CHR':chrom,'POS': {'$gte':start1,'$lte': end1},'VARIANT_INFO.CHR2':chrom2, 'VARIANT_INFO.END':{'$gte':start2,'$lte':end2},'VARIANT_INFO.SVTYPE':svtype,'VARIANT_INFO.CT':ct },
	  { 'CHR':chrom2,'POS': {'$gte':start2,'$lte': end2},'VARIANT_INFO.CHR2':chrom, 'VARIANT_INFO.END':{'$gte':start1,'$lte':end1},'VARIANT_INFO.SVTYPE':svtype,'VARIANT_INFO.CT':ct2 }
	] }
 
      if q:
	q = qu.create(q)
	dq = eval(q)
	query.update(dq)
      
      if 'SAMPLES.NAME' in query:
	if '$nin' in query['SAMPLES.NAME']:
	  query['SAMPLES.NAME']['$nin'] += samples
	else:
	  query['SAMPLES.NAME']['$nin'] = samples
      else:
	query['SAMPLES.NAME'] = { '$nin': samples }

      hits = db.variants.find_one(query)
                  
      if ( not hits ):
	print line
      else:
	if fields[6] != "PASS":
	  fields[6] = fields[6]+",DB"
	else:
	  fields[6] = "DB"
	print "\t".join(fields) 

