# These tests are designed to assist in the development of the Brand Spend Data Model

import unittest
import pandas as pd
import utils
import os
import os.path
import channels
import win32com.client
import assemblers

class util_tester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assumption = utils.assumptions()
# Utils
    def test_logger_type(self):
        self.assertIsInstance(utils.logger(),str)

    def test_assumption_types(self):
        self.assertIsInstance(self.assumption["root"],str)
        self.assertIsInstance(self.assumption["source"],str)
        self.assertIsInstance(self.assumption["target"],str)
        self.assertIsInstance(self.assumption["imp"],pd.DataFrame)
        self.assertIsInstance(self.assumption["budget"],pd.DataFrame)
    
    def test_file_gatherer_type(self):
        self.assertIsInstance(utils.file_gatherer(source=self.assumption["source"],criteria=".*"),list)

    def test_data_framer_xlsx_type(self):
        self.assertIsInstance(utils.data_framer(source = self.assumption["source"]
                                                , files = utils.file_gatherer(source = self.assumption["source"],
                                                                            criteria = 'COCO.*')
                                                , sheets = ["COCO FINAL"]
                                                , skiprows = None),pd.DataFrame)
    def test_data_framer_csv_type(self):
        self.assertIsInstance(utils.data_framer(source = self.assumption["source"]
                                                , files = utils.file_gatherer(source = self.assumption["source"],
                                                                            criteria = 'spend\.csv')
                                                , sheets = None
                                                , skiprows = None),pd.DataFrame)
        # CANNOT BE RUN IN LINUX
    # def test_dla_mail_retrieval(self):
    #     tester = utils.dla_mail_retrieval(self.assumption["source"]).info
    #     self.assertIsInstance(tester[0],str)
    #     self.assertIsInstance(tester[1],win32com.client.CDispatch)
    #     self.assertIsInstance(tester[2],win32com.client.CDispatch)
    #     self.assertIsInstance(tester[3],win32com.client.CDispatch)
    #     self.assertIsInstance(tester[4],win32com.client.CDispatch)
    #     self.assertIsInstance(tester[5],win32com.client.CDispatch)
    #     self.assertIsInstance(tester[6],str)


# Channels
    def test_coco(self):
        self.assertIsInstance(channels.coco(self.assumption['source']),pd.DataFrame)

    def test_mlb(self):
        self.assertIsInstance(channels.mlb(self.assumption['source']),pd.DataFrame)

    def test_nascar(self):
        self.assertIsInstance(channels.nascar(self.assumption['source']),pd.DataFrame)
    
    def test_pr(self):
        self.assertIsInstance(channels.pr(self.assumption['source']),pd.DataFrame)

    def test_raiders(self):
        self.assertIsInstance(channels.raiders(self.assumption['source']),pd.DataFrame)

    def test_vgk(self):
        self.assertIsInstance(channels.vgk(self.assumption['source']),pd.DataFrame)

    def test_wso(self):
        self.assertIsInstance(channels.wso(self.assumption['source']),pd.DataFrame)
        
    def test_wwe(self):
        self.assertIsInstance(channels.wwe(self.assumption['source']),pd.DataFrame)

    def test_youtube(self):
        self.assertIsInstance(channels.youtube(self.assumption['source']),pd.DataFrame)

    def test_tv(self):
        self.assertIsInstance(channels.tv(self.assumption['source']),pd.DataFrame)
    
    def test_digital(self):
        self.assertIsInstance(channels.digital(self.assumption['source']),pd.DataFrame)
    
    def test_adelaide(self):
        self.assertIsInstance(channels.adelaide(self.assumption['source'],self.assumption['target'])[1],pd.DataFrame)
        self.assertIsInstance(channels.adelaide(self.assumption['source'],self.assumption['target'])[2],pd.DataFrame)

    def test_videoamp(self):
        va = channels.videoamp(self.assumption['source'],self.assumption['target'])
        self.assertIsInstance(va[0],pd.DataFrame)
        self.assertIsInstance(va[1],pd.DataFrame)
    
    def test_social_no_api(self):
        self.assertIsInstance(channels.social_no_api(self.assumption['source']),pd.DataFrame)

# Facebook API

# Assemblers

    def test_sponsorship(self):
        self.assertIsInstance(assemblers.sponsorship(self.assumption['source']),pd.DataFrame)

    def test_master(self):
        result = assemblers.master()
        self.assertIsInstance(result,tuple)
        self.assertIsInstance(result[0],pd.DataFrame)
        self.assertIsInstance(result[1],pd.DataFrame)



    def test_budget_distribution(self):
        self.assertIsInstance(assemblers.budget_distribution(assemblers.master()),pd.DataFrame)

    def test_imp_assignment(self):
        self.assertIsInstance(assemblers.imp_assignment(assemblers.budget_distribution(assemblers.master())),pd.DataFrame)
        
    def test_output(self):
        self.assertTrue(os.path.isfile(os.path.join(self.assumption['target'],r'BrandBudget.csv')))
        self.assertTrue(os.path.isfile(os.path.join(self.assumption['target'],r'BrandSpendMaster.csv')))
        self.assertTrue(os.path.isfile(os.path.join(self.assumption['target'],r"adelaide_data.csv")))
        self.assertTrue(os.path.isfile(os.path.join(self.assumption['target'],r"monthly_site_visits_by_partner.csv")))
        self.assertTrue(os.path.isfile(os.path.join(self.assumption['target'],r"Meta_Data_by_Placement.csv")))

if __name__ == '__main__':
    unittest.main()