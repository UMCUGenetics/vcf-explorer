import unittest

import bson

import utils.vcf

class GatkVCFImportTestCase(unittest.TestCase):
    def test_gatk_header_line(self):
        vcf_header_input = '#CHROM\tPOS\tid\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t1\t2\t3\t4'
        vcf_header_output = {'samples':['1','2','3','4']}
        self.assertEqual(utils.vcf.gatk_header(vcf_header_input),vcf_header_output)

    def test_gatk_snp_line(self):
        vcf_line_input = '1\t69511\trs75062661\tA\tG\t6448.36\tPASS\tAC=8;AF=1.00;AN=8;DB;DP=233;FS=0.000;MLEAC=8;MLEAF=1.00;MQ=40.45;QD=27.68;SOR=1.083\tGT:AD:DP:GQ:PL\t1/1:0,48:48:99:1371,144,0\t1/1:0,94:94:99:2511,281,0\t1/1:0,9:9:27:294,27,0\t1/1:0,82:82:99:2298,246,0'
        vcf_metadata_input = {'_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'samples':['1','2','3','4']}
        vcf_line_result = ({'chr': '1', 'pos': 69511, 'ref': 'A', 'alt': 'G', 'dbSNP': 'rs75062661'},
            [{'sample_name':'1', 'vcf_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'GT':'1/1', 'AD':'0,48', 'DP':'48', 'GQ':'99', 'PL':'1371,144,0'},
            {'sample_name':'2', 'vcf_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'GT':'1/1', 'AD':'0,94', 'DP':'94', 'GQ':'99', 'PL':'2511,281,0'},
            {'sample_name':'3', 'vcf_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'GT':'1/1', 'AD':'0,9', 'DP':'9', 'GQ':'27', 'PL':'294,27,0'},
            {'sample_name':'4', 'vcf_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'GT':'1/1', 'AD':'0,82', 'DP':'82', 'GQ':'99', 'PL':'2298,246,0'},
        ])

        self.assertEqual(utils.vcf.gatk_line(vcf_line_input,vcf_metadata_input),vcf_line_result)

class DellyVCFImportTestCase(unittest.TestCase):
    def test_delly_header_line(self):
        vcf_header_input = '#CHROM\tPOS\tid\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t1\t2\t3\t4'
        vcf_header_output = {'samples':['1','2','3','4']}
        self.assertEqual(utils.vcf.delly_header(vcf_header_input),vcf_header_output)

    def test_delly_snp_line(self):
        vcf_line_input = '1\t21492484\tDEL00000120\tN\t<DEL>\t0\tPASS\t"IMPRECISE;CIEND=-317,317;CIPOS=-317,317;SVtype=DEL;SVMETHOD=EMBL.DELLYv0.6.7;CHR2=1;END=149337534;CT=3to5;INSLEN=0;PE=3;MAPQ=42"\tGT:GL:GQ:FT:RCL:RC:RCR:CN:DR:DV:RR:RV\t0/1:-2.90075,0,-132.871:29:PASS:4249861:24362177:14135397:3:26:3:0:0\t0/0:0,-5.11741,-98.5999:51:PASS:4920660:27959714:16156110:3:17:0:0:0\t0/0:0,-5.95897,-80.3384:60:PASS:4627520:26546097:15423242:3:20:0:0:0'
        vcf_metadata_input = {}
        vcf_metadata_input = {
            '_id':bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'),
            "header": {
                "info": [
                    { "description" : "pe confidence interval around end", "type": "integer", "id" : "ciend", "number" : "2" },
                    { "description" : "peconfidence interval around pos", "type" : "integer", "id" : "cipos","number" : "2" },
                    { "description" : "chromosome for end coordinate incase of a translocation", "type" : "string", "id" : "chr2", "number" :"1" },
                    { "description" : "end position of the structural variant","type" : "integer", "id" : "end", "number" : "1" },
                    { "description" : "paired-end support of the structural variant", "type" : "integer", "id": "pe", "number" : "1" },
                    { "description" : "median mapping quality of paired-ends", "type" : "integer", "id" : "mapq", "number" : "1" },
                    { "description" : "split-read support", "type" : "integer", "id" : "sr","number" : "1" },
                    { "description" : "split-read consensus alignment quality", "type" : "float", "id" : "srq", "number" : "1" },
                    { "description" : "split-read consensus sequence", "type" : "string", "id": "consensus", "number" : "1" },
                    { "description" : "paired-end signature induced connection type", "type" : "string", "id" : "ct", "number" : "1"},
                    { "description" : "imprecise structural variation", "type" : "flag","id" : "imprecise", "number" : "0" },
                    { "description" : "precise structural variation", "type" : "flag", "id" : "precise", "number" : "0"},
                    { "description" : "type of structural variant", "type" : "string","id" : "svtype", "number" : "1" },
                    { "description" : "type of approach used to detect sv", "type" : "string", "id" : "svmethod", "number" : "1"},
                    { "description" : "predicted length of the insertion", "type" :"integer", "id" : "inslen", "number" : "1" }
                    ],
                "format": [
                    { "description" : "genotype", "type" :"string", "id" : "gt", "number" : "1" },
                    { "description" : "log10-scaled genotype likelihoods for rr,ra,aa genotypes", "type" : "float", "id" :"gl", "number" : "g" },
                    { "description" : "genotype quality", "type" :"integer", "id" : "gq", "number" : "1" },
                    { "description" : "per-samplegenotype filter", "type" : "string", "id" : "ft", "number" : "1" },
                    { "description" : "raw high-quality read counts for the sv", "type" :"integer", "id" : "rc", "number" : "1" },
                    { "description" : "rawhigh-quality read counts for the left control region", "type" :"integer", "id" : "rcl", "number" : "1" },
                    { "description" : "rawhigh-quality read counts for the right control region", "type" :"integer", "id" : "rcr", "number" : "1" },
                    { "description" : "read-depth based copy-number estimate for autosomal sites", "type" : "integer", "id" : "cn", "number" : "1" },
                    { "description" : "# high-quality reference pairs", "type" : "integer", "id" : "dr", "number" : "1" },
                    { "description" : "# high-quality variant pairs", "type" : "integer", "id": "dv", "number" : "1" },
                    { "description" : "# high-quality reference junction reads", "type" : "integer", "id" : "rr", "number" : "1" },
                    { "description" : "# high-quality variant junction reads", "type" :"integer", "id" : "rv", "number" : "1" }
                    ]
                },
            'samples':['1','2','3']
        }
        vcf_line_result = ({'variant_info': {'svtype': 'del', 'end': 149337534, 'chr2': '1', 'ct': '3to5'}, 'pos': 21492484, 'qual': '0', 'chr': '1', 'alt': '<DEL>', 'ref': 'N', 'id': 'DEL00000120'},
         [{'filter': 'PASS', 'vcf_id': bson.objectid.ObjectId('5694bd9e6c9d8b15869320fe'), 'format': {'rv': 0, 'gt': '0/1', 'ft': 'PASS', 'cn': 3, 'gq': 29, 'rcr': 14135397, 'rr': 0, 'rcl': 4249861, 'rc': 24362177, 'dv': 3, 'gl': '-2.90075,0,-132.871', 'dr': 26}, 'info': {'precise': '"IMPRECISE', 'ciend': '-317,317', 'cipos': '-317,317', 'mapq': '42"', 'pe': 3, 'inslen': 0}, 'sample_name': '1'}])

        self.assertEqual(utils.vcf.delly_line(vcf_line_input,vcf_metadata_input),vcf_line_result)

if __name__ == '__main__':
    unittest.main()
