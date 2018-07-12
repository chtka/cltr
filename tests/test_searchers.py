import sys
import os
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import unittest
import json

from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.clinical_trials_searcher import ClinicalTrialsSearcher
from searchers.isrctn_searcher import ISRCTNSearcher

from scripts.search_trials import run_search_trials

class TestSearchers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fake_config = {
            "bucket_names": {
                "raw_data_bucket_name": "fake_raw_data_bucket",
                "processed_data_bucket_name": "fake_processed_data_bucket"
            },
            "search_terms_file_path": path.join(path.dirname(path.abspath(__file__)), 'test_data/search_terms_short.txt'),
            "searchers": ["clinical-trials-gov"]
        }

        cls.fake_config_filepath = path.join(path.dirname(path.abspath(__file__)), 'test_data/config.json')

        with open(cls.fake_config_filepath, 'w') as fake_config_file:
            json.dump(fake_config, fake_config_file)
            

    def test_clinical_trials_searcher(self):
        QUERY = "The Sleep, Liver Evaluation and Effective Pressure Study"
        DOWNLOAD_FILE_FORMAT = "clinical_trials_gov_results_%s.zip"

        try:
            with ClinicalTrialsSearcher() as searcher:
                filepath = searcher.search_and_download_raw(QUERY)
                
                self.assertTrue(path.exists(DOWNLOAD_FILE_FORMAT % QUERY))
                self.assertEqual(filepath, DOWNLOAD_FILE_FORMAT % QUERY)
        finally:
            if path.exists(DOWNLOAD_FILE_FORMAT % QUERY):
                os.remove(DOWNLOAD_FILE_FORMAT % QUERY)

    def test_anzctr_searcher(self):
        QUERY = "ACTRN12618000904279p"
        DOWNLOAD_FILE_FORMAT = "anzctr_results_%s.zip"

        try:
            with ANZCTRSearcher() as searcher:
                filepath = searcher.search_and_download_raw(QUERY)

                self.assertTrue(path.exists(DOWNLOAD_FILE_FORMAT % QUERY))
                self.assertEqual(filepath, DOWNLOAD_FILE_FORMAT % QUERY)
        finally:
            if path.exists(DOWNLOAD_FILE_FORMAT % QUERY):
                os.remove(DOWNLOAD_FILE_FORMAT % QUERY)

    def test_search_trials_script(self):

        run_search_trials(self.fake_config_filepath, no_upload=True)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.fake_config_filepath)




