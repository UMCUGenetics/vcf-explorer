import unittest

import bson

import utils.vcf

class GatkVCFImportTestCase(unittest.TestCase):
    def test_gatk_header_line(self):
        vcf_header_input = '#CHROM\tPOS\tid\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t1\t2\t3\t4'
        vcf_header_output = {'samples':['1','2','3','4']}
        self.assertEqual(utils.vcf.vcf_header(vcf_header_input),vcf_header_output)

    def test_gatk_snp_line(self):
        vcf_line_input = '1\t69511\trs75062661\tA\tG\t6448.36\tPASS\tAC=8;AF=1.00;AN=8;DB;DP=233;FS=0.000;MLEAC=8;MLEAF=1.00;MQ=40.45;QD=27.68;SOR=1.083\tGT:AD:DP:GQ:PL\t1/1:0,48:48:99:1371,144,0\t1/1:0,94:94:99:2511,281,0\t1/1:0,9:9:27:294,27,0\t1/1:0,82:82:99:2298,246,0'
        vcf_metadata_input = {
            '_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'),
            'samples':['1','2','3','4'],
            "FORMAT" : {
                "GT" : { "type" : "String","number" : "1", "description" : "Genotype" },
                "GQ" : { "type" : "Integer", "number" : "1", "description" : "Genotype Quality" },
                "AD" : { "type" : "Integer", "number" : ".", "description" : "Allelic depths for the ref and alt alleles in the order listed" },
                "DP" : { "type" : "Integer", "number" : "1", "description" : "Approximate read depth (reads with MQ=255 or with bad mates are filtered)" },
                "PL" : { "type" : "Integer", "number" : "G", "description" : "Normalized, Phred-scaled likelihoods for genotypes as defined in the VCF specification" }
            }
        }
        vcf_line_result = ({'chr': '1', 'pos': 69511, 'ref': 'A', 'alt': 'G', 'dbSNP': 'rs75062661'},
        [
            {'sample':'1', 'vcf_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'genotype' : {'GT':'1/1', 'AD':[0,48], 'DP':48, 'GQ':99, 'PL':[1371,144,0]} },
            {'sample':'2', 'vcf_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'genotype' : {'GT':'1/1', 'AD':[0,94], 'DP':94, 'GQ':99, 'PL':[2511,281,0]} },
            {'sample':'3', 'vcf_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'genotype' : {'GT':'1/1', 'AD':[0,9], 'DP':9, 'GQ':27, 'PL':[294,27,0]} },
            {'sample':'4', 'vcf_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'genotype' : {'GT':'1/1', 'AD':[0,82], 'DP':82, 'GQ':99, 'PL':[2298,246,0]} },
        ])

        self.assertEqual(utils.vcf.gatk_line(vcf_line_input,vcf_metadata_input),vcf_line_result)

class DellyVCFImportTestCase(unittest.TestCase):
    def test_delly_header_line(self):
        vcf_header_input = '#CHROM\tPOS\tid\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t1\t2\t3\t4'
        vcf_header_output = {'samples':['1','2','3','4']}
        self.assertEqual(utils.vcf.vcf_header(vcf_header_input),vcf_header_output)

    def test_delly_snp_line(self):
        vcf_line_input = '1\t21492484\tDEL00000120\tN\t<DEL>\t0\tPASS\tIMPRECISE;CIEND=-317,317;CIPOS=-317,317;SVtype=DEL;SVMETHOD=EMBL.DELLYv0.6.7;CHR2=1;END=149337534;CT=3to5;INSLEN=0;PE=3;MAPQ=42\tGT:GL:GQ:FT:RCL:RC:RCR:CN:DR:DV:RR:RV\t0/1:-2.90075,0,-132.871:29:PASS:4249861:24362177:14135397:3:26:3:0:0\t0/0:0,-5.11741,-98.5999:51:PASS:4920660:27959714:16156110:3:17:0:0:0\t0/0:0,-5.95897,-80.3384:60:PASS:4627520:26546097:15423242:3:20:0:0:0'
        vcf_metadata_input = {}
        vcf_metadata_input = {
            '_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'),
            "INFO" : {
                "PRECISE" : { "type" : "Flag", "number" : "0", "description" : "Precise structural variation" },
                "SVMETHOD" : { "type" : "String", "number" : "1", "description" : "Type of approach used to detect SV" },
                "CIEND" : { "type" : "Integer", "number" : "2", "description" : "PE confidence interval around END" },
                "END" : { "type" : "Integer", "number" : "1", "description" : "End position of the structural variant" },
                "CHR2" : { "type" : "String", "number" : "1", "description" : "Chromosome for END coordinate in case of a translocation" },
                "SR" : { "type" : "Integer", "number" : "1", "description" : "Split-read support" },
                "SRQ" : { "type" : "Float", "number" : "1", "description" : "Split-read consensus alignment quality" },
                "CIPOS" : { "type" : "Integer", "number" : "2", "description" : "PE confidence interval around POS" },
                "CONSENSUS" : { "type" : "String", "number" : "1", "description" : "Split-read consensus sequence" },
                "SVTYPE" : { "type" : "String", "number" : "1", "description" : "Type of structural variant" },
                "MAPQ" : { "type" : "Integer", "number" : "1", "description" : "Median mapping quality of paired-ends" },
                "PE" : { "type" : "Integer", "number" : "1", "description" : "Paired-end support of the structural variant" },
                "INSLEN" : { "type" : "Integer", "number" : "1", "description" : "Predicted length of the insertion" },
                "IMPRECISE" : { "type" : "Flag", "number" : "0", "description" : "Imprecise structural variation" },
                "CT" : { "type" : "String", "number" : "1", "description" : "Paired-end signature induced connection type"}
            },
            "FORMAT" : {
                "RV" : { "type" : "Integer", "number" : "1", "description" : "# high-quality variant junction reads" },
                "GT" : { "type" : "String", "number" : "1", "description" : "Genotype" },
                "FT" : { "type" : "String", "number" : "1", "description" : "Per-sample genotype filter" },
                "CN" : { "type" : "Integer", "number" : "1", "description" : "Read-depth based copy-number estimate for autosomal sites" },
                "GQ" : { "type" : "Integer", "number" : "1", "description" : "Genotype Quality" },
                "RR" : { "type" : "Integer", "number" : "1", "description" : "# high-quality reference junction reads" },
                "RCR" : { "type" : "Integer", "number" : "1", "description" : "Raw high-quality read counts for the right control region" },
                "RCL" : { "type" : "Integer", "number" : "1", "description" : "Raw high-quality read counts for the left control region" },
                "RC" : { "type" : "Integer", "number" : "1", "description" : "Raw high-quality read counts for the SV" },
                "DV" : { "type" : "Integer", "number" : "1", "description" : "# high-quality variant pairs" },
                "GL" : { "type" : "Float", "number" : "G", "description" : "Log10-scaled genotype likelihoods for RR,RA,AA genotypes" },
                "DR" : { "type" : "Integer", "number" : "1", "description" : "# high-quality reference pairs"}
        },
            'samples':['1','2','3']
        }
        vcf_line_result = ({'END': 149337534, 'CHR2': '1', 'pos': 21492484, 'chr': '1', 'alt': '<DEL>', 'ref': 'N', 'id': 'DEL00000120', 'CT': '3to5'},
         [{'sample': '1', 'vcf_id': bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'info': {'PRECISE': 'IMPRECISE', 'CIEND': [-317, 317], 'CIPOS': [-317, 317], 'MAPQ': 42, 'PE': 3, 'INSLEN': 0}, 'filter': 'PASS', 'genotype': {'RV': 0, 'GT': '0/1', 'FT': 'PASS', 'CN': 3, 'GQ': 29, 'RR': 0, 'RCR': 14135397, 'RCL': 4249861, 'RC': 24362177, 'DV': 3, 'GL': [-2.90075, 0.0, -132.871], 'DR': 26}}]
         )

        self.assertEqual(utils.vcf.delly_line(vcf_line_input,vcf_metadata_input),vcf_line_result)

if __name__ == '__main__':
    unittest.main()
