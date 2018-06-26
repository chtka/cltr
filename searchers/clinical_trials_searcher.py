import os
from os import path
import pandas as pd
from time import sleep
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import zipfile

from searchers.searcher import Searcher
from selenium.common.exceptions import NoSuchElementException


class ClinicalTrialsSearcher(Searcher):
    
    CLINICAL_TRIALS_BASE_URL = "https://clinicaltrials.gov/ct2/results?"
    SEARCH_RESULTS_ZIP_FILE_NAME = "search_result.zip"
    
    def search_and_download_raw(self, search_term):
        
        # delete old file if it exists
        if path.exists(self.SEARCH_RESULTS_ZIP_FILE_NAME):
            os.remove(self.SEARCH_RESULTS_ZIP_FILE_NAME)
        
        # perform search and download zip archive of all matching studies
        self.browser.get(self.CLINICAL_TRIALS_BASE_URL + urlencode({"term": search_term}))

        try:
            self.browser.find_element_by_id('downloadAdvancedForm').submit()
            
            # wait for the zip archive to download; for some reason there has to be a delay, else the zip file will not finish
            # downloading correctly...
            while (not path.exists(self.SEARCH_RESULTS_ZIP_FILE_NAME)) or (not zipfile.is_zipfile(self.SEARCH_RESULTS_ZIP_FILE_NAME)):
                sleep(.1)

            os.rename(self.SEARCH_RESULTS_ZIP_FILE_NAME, "clinical_trials_gov_results_%s.zip" % search_term)

            return "clinical_trials_gov_results_%s.zip" % search_term
        except NoSuchElementException:
            return None
