import lxml
import os
import pandas as pd
import requests
import zipfile

from bs4 import BeautifulSoup
from glob import glob
from os import path
from time import sleep
from urllib.parse import urlencode
from selenium.common.exceptions import NoSuchElementException
from searchers.searcher import Searcher

class ISRCTNSearcher(Searcher):
    """
    A Searcher class that uses a Selenium driver for Mozilla Firefox to query
    the ISRCTN registry and download the search results for the 
    clinical trials matching the query.

    The results from the ISRCTN registry come in the form of a csv file, where
    each row contains the data for a clinical trial that matches the query.
    """
        
    # define URLs
    ISRCTN_SEARCH_URL = "http://www.isrctn.com/search?"
    ISRCTN_BASE_URL = "http://www.isrctn.com/"
    
    def search_and_download_raw(self, search_term, format="parquet"):
        """
        Searches the ISRCTN registry for clinical trials matching the
        specified search term.

        Args:
            search_term: The search term for which to search 
            the ISRCTRN registry.

        Returns:
            string: The filepath to the downloaded raw data.
        """        
        # download file path changes dynamically based on search term, so we 
        # cannot pre-define it
        RESULTS_CSV_FILE_NAME = 'ISRCTN search results for %s.csv'\
            % search_term
        
        # delete old file if it exists
        if path.exists(RESULTS_CSV_FILE_NAME):
            os.remove(RESULTS_CSV_FILE_NAME)
            
        # perform search and download csv file of all matching studies
        self.browser.get(self.ISRCTN_SEARCH_URL + urlencode(
            {
                "q": search_term
            }
        ))

        # encased in try-except block in case no results are found
        try:
            self.browser.find_element_by_id('opener').click()
            self.browser.find_element_by_id('select-all').click()
            self.browser.find_element_by_class_name('download-csv').click()
            
            # wait for the csv file to download
            while (not path.exists(RESULTS_CSV_FILE_NAME)) or path.exists(RESULTS_CSV_FILE_NAME + '.part'):
                sleep(.1)
            

            print(RESULTS_CSV_FILE_NAME)
            # read the csv file into a DataFrame
            df = pd.read_csv(RESULTS_CSV_FILE_NAME)
            
            # function for making HTTP requests for the given ISRCTN number to 
            # retrieve principal investigator and number of sites
            def get_extra_attrs(isrctn_ser):

                print("Getting extra info for", isrctn_ser)

                r = requests.get("http://www.isrctn.com/%s" % isrctn_ser)

                soup = BeautifulSoup(r.text, "lxml")

                # principal investigator
                pi = soup.find('h3', string="Primary contact")\
                    .find_next_sibling('p').text.strip()

                # number_of_sites
                nos = len(soup.find_all('h3', 
                    string="Trial participating centre"))

                return (pi, nos)
            
            # convert to DataFrame and join the DataFrames
            df2 = pd.DataFrame(df['ISRCTN'].apply(get_extra_attrs)\
                .values.tolist())
            df2 = df2.rename(columns=
                {
                    0: 'principal_investigator', 1: 'number_of_sites'
                }
            )
            
            df.index = df2.index
            
            df = df.join(df2)
            
            # delete the file
            os.remove(RESULTS_CSV_FILE_NAME)

            # return DataFrame for more processing
            
            if format == "csv":
                df.to_csv("isrctn_results_%s.csv" % search_term)
                return "isrctn_results_%s.csv" % search_term
            else:
                df.to_parquet("isrctn_results_%s.parquet" % search_term)
                return "isrctn_results_%s.parquet" % search_term
        except NoSuchElementException:
            return None

        