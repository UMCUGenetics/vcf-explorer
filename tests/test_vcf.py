import unittest

import utils.vcf

class GatkVCFImportTestCase(unittest.TestCase):
    def test_gatk_header_line(self):
        vcf_header_input = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t1\t2\t3\t4'
        vcf_header_output = {'samples':['1','2','3','4']}
        self.assertEqual(utils.vcf.gatk_header(vcf_header_input),vcf_header_output)

    def test_snp_line(self):
        vcf_line_input = '1\t69511\trs75062661\tA\tG\t6448.36\tPASS\tAC=8;AF=1.00;AN=8;DB;DP=233;FS=0.000;MLEAC=8;MLEAF=1.00;MQ=40.45;QD=27.68;SOR=1.083\tGT:AD:DP:GQ:PL\t1/1:0,48:48:99:1371,144,0\t1/1:0,94:94:99:2511,281,0\t1/1:0,9:9:27:294,27,0\t1/1:0,82:82:99:2298,246,0'
        vcf_sample_input = {'run':'test', 'samples':['1','2','3','4']}
        vcf_line_result = ({'chr': '1', 'pos': 69511, 'ref': 'A', 'alt': 'G', 'dbSNP': 'rs75062661'},
            [{'id':'1', 'GT':'1/1', 'AD':'0,48', 'DP':'48', 'GQ':'99', 'PL':'1371,144,0'},
            {'id':'2', 'GT':'1/1', 'AD':'0,94', 'DP':'94', 'GQ':'99', 'PL':'2511,281,0'},
            {'id':'3', 'GT':'1/1', 'AD':'0,9', 'DP':'9', 'GQ':'27', 'PL':'294,27,0'},
            {'id':'4', 'GT':'1/1', 'AD':'0,82', 'DP':'82', 'GQ':'99', 'PL':'2298,246,0'},
        ])

        self.assertEqual(utils.vcf.gatk_line(vcf_line_input,vcf_sample_input),vcf_line_result)

if __name__ == '__main__':
    unittest.main()
