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


from searchers.searcher import Searcher

class ISRCTNSearcher(Searcher):
    
    ISRCTN_SEARCH_URL = "http://www.isrctn.com/search?"
    ISRCTN_BASE_URL = "http://www.isrctn.com/"
    
    def search_and_load_df(self, searchTerm):
        
        def strip_str_list_els(els):
            return list(map(str.strip, els))
        
        # download file path changes dynamically based on search term, so we cannot pre-define it
        RESULTS_CSV_FILE_NAME = 'ISRCTN search results for %s.csv' % searchTerm
        
        # delete old file if it exists
        if path.exists(RESULTS_CSV_FILE_NAME):
            os.remove(RESULTS_CSV_FILE_NAME)
            
        # perform search and download csv file of all matching studies
        self.browser.get(self.ISRCTN_SEARCH_URL + urlencode({"q": searchTerm}))
        self.browser.find_element_by_id('opener').click()
        self.browser.find_element_by_id('select-all').click()
        self.browser.find_element_by_class_name('download-csv').click()
        
        # wait for the csv file to download
        while not path.exists(RESULTS_CSV_FILE_NAME):
            sleep(.1)
        
        # read the csv file into a DataFrame
        df = pd.read_csv(RESULTS_CSV_FILE_NAME)
        
        df = df.rename(index=str, columns={'Sponsor': 'lead_sponsor', 'Overall trial end': 'estimated_completion_date', 'ISRCTN': 'ct_id', 'Overall trial status': 'status', 'Title': 'title'})
        
        df['collaborators'] = (df['Funder'].str.split(';').apply(strip_str_list_els).apply(set) - df['lead_sponsor'].apply(lambda s: {s})).apply(list)
        
        df = df[['ct_id', 'title', 'status', 'lead_sponsor', 'collaborators', 'estimated_completion_date']]
        
        def get_extra_attrs(isrctn_ser):

            r = requests.get("http://www.isrctn.com/" + isrctn_ser)

            soup = BeautifulSoup(r.text, "lxml")

            # principal investigator
            pi = soup.find('h3', string="Primary contact").find_next_sibling('p').text.strip()

            # number_of_sites
            nos = len(soup.find_all('h3', string="Trial participating centre"))

            return (pi, nos)
        
        df2 = pd.DataFrame(df['ct_id'].apply(get_extra_attrs).values.tolist())
        df2 = df2.rename(columns={0: 'principal_investigator', 1: 'number_of_sites'})
        
        df.index = df2.index
        
        df = df.join(df2)
        df = df[['ct_id', 'title', 'status', 'principal_investigator', 'number_of_sites', 'lead_sponsor', 'collaborators', 'estimated_completion_date']]
        
        os.remove(RESULTS_CSV_FILE_NAME)

        return df