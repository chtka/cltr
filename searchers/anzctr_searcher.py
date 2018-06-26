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

        # # open the zip archive
        # archive = zipfile.ZipFile(archive_name, 'r')
        
        # # initialize DataFrame for holding the extracted data
        # df = pd.DataFrame(columns=[
        #     'ct_id', 
        #     'title', 
        #     'status', 
        #     'principal_investigator', 
        #     'number_of_sites', 
        #     'lead_sponsor', 
        #     'collaborators', 
        #     'estimated_completion_date'
        # ])
        
        # # iterating through all files in the archive, we extract the wanted data
        # for filename in [name for name in archive.namelist() 
        #     if name.endswith('.xml')]:
            
        #     # open and read file contents into string
        #     file = archive.open(filename)
        #     file_as_string = file.read()
            
        #     # create XML tree
        #     root = lxml.etree.fromstring(file_as_string)
            
        #     lxml.etree.fromstring(file_as_string)

        #     # get all desired data
            
        #     # actr_number/nct_id
        #     actr_number_list = root.xpath('./actrnumber/text()')
            
        #     if len(actr_number_list) == 0:
        #         ct_id = root.xpath('./nctid/text()')[0]
        #     else:
        #         ct_id = actr_number_list[0]
            
        #     # title
        #     title = root.xpath('./trial_identification/studytitle/text()')[0]
            
        #     # status
        #     status = root.xpath('./stage/text()')[0]
            
        #     # principal_investigator
        #     principal_investigator = root\
        #         .xpath(
        #             './/type[text()="Principal Investigator"]/../name/text()'
        #         )[0] if len(root.xpath(
        #             './/type[text()="Principal Investigator"]/../name/text()'
        #         )) != 0 else ""
            
        #     # number_of_sites
        #     number_of_sites = 0
            
        #     # lead_sponsor
        #     lead_sponsor = root.xpath('.//primarysponsorname/text()')[0]
            
        #     # collaborators - defined as all funding sources and collaborators (minus the primary sponsor)
        #     collaborators = list((set(root.xpath('.//fundingsource/fundingname/text()')) |
        #                          set(root.xpath('.//othercollaborator/othercollaboratorname/text()'))) - {lead_sponsor})
            
        #     # estimated_completion_date - ANZCTR does not provide completion dates, only submission and approval dates
        #     estimated_completion_date = "Unknown"
            
        #     row = pd.Series({
        #         "ct_id": ct_id, 
        #         "title": title, 
        #         "status": status, 
        #         "principal_investigator": principal_investigator,
        #         "number_of_sites": number_of_sites, 
        #         "lead_sponsor": lead_sponsor, 
        #         "collaborators": collaborators,
        #         "estimated_completion_date": estimated_completion_date
        #     })
            
        #     # insert row into DataFrame
        #     df = df.append(row, ignore_index=True)
            
        #     # close the current file
        #     file.close()
            
        # # close and delete the archive
        # archive.close()
        # os.remove(archive_name)
        
        # # return the DataFrame for further processing
        # return df