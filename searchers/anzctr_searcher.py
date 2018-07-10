import lxml
import os
import pandas as pd
import zipfile
from selenium.common.exceptions import NoSuchElementException

from glob import glob
from os import path
from time import sleep
from urllib.parse import urlencode


from searchers.searcher import Searcher

class ANZCTRSearcher(Searcher):
    """
    A Searcher class that uses a Selenium driver for Mozilla Firefox to query
    the ANZCTR site and download the search results for the 
    clinical trials matching the query.

    The results from the ANZCTR site come in the form of a zip archive of
    XML files, one for each clinical trial matching the query.
    """
    
    ANZCTR_BASE_URL = "http://www.anzctr.org.au/TrialSearch.aspx?"
    
    def search_and_download_raw(self, search_term):
        """
        Searches the ANZCTR site for clinical trials matching the
        specified search term.

        Args:
            search_term: The search term for which to search 
            the ANZCTR site.

        Returns:
            string: The filepath to the downloaded raw data.
        """        

        # data comes in this name format
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

        try:

            # find and click the download button, if it exists
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

        except NoSuchElementException as e:
            print(e)
            return None