import sys
import os
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import unittest

from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.clinical_trials_searcher import ClinicalTrialsSearcher
from searchers.isrctn_searcher import ISRCTNSearcher

class TestSearchers(unittest.TestCase):

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


