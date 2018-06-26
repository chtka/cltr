import lxml
import os
import pandas as pd
import zipfile

from glob import glob
from os import path
from time import sleep
from urllib.parse import urlencode


from searchers.searcher import Searcher

class ANZCTRSearcher(Searcher):
    
    ANZCTR_BASE_URL = "http://www.anzctr.org.au/TrialSearch.aspx?"
    
    def search_and_download_raw(self, search_term):
        
        SEARCH_RESULTS_ZIP_FILE_GLOB_PATTERN = path.join(os.getcwd(),
            'TrialDetails*')
        
        # delete all old zip archives if they exist
        matching_files = glob(SEARCH_RESULTS_ZIP_FILE_GLOB_PATTERN)
        if len(matching_files) != 0:
            for matching_file in matching_files:
                os.remove(matching_file)
        
        
        # perform search and download zip archive of all matching studies
        self.browser.get(self.ANZCTR_BASE_URL + urlencode({
            "searchTxt": search_term, 
            "isBasic": "True"
        }))
        self.browser.find_element_by_id('ctl00_body_btnDownload').click()
        
        archive_name = ""
        
        # wait for the zip archive to download
        while True:
            matching_files = glob(SEARCH_RESULTS_ZIP_FILE_GLOB_PATTERN)
            if len(matching_files) != 0 and zipfile.is_zipfile(matching_files[0]):

                archive_name = matching_files[0]
                break
            sleep(.1)

        os.rename(archive_name, "anzctr_results_%s.zip" % search_term)

        return "anzctr_results_%s.zip" % search_term