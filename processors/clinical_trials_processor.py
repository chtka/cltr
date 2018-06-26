import xml.etree.ElementTree as ET

import pandas as pd
import zipfile

from processors.processor import Processor

class ClinicalTrialsProcessor(Processor):
    """ 
    Processes the zip archives downloaded from the ClinicalTrials.gov results
    pages. 
    """

    def process_and_load_df(self, filepath_or_buffer):
        """
        Processes the zip archive; returns a pandas DataFrame containing the
        processed data.

        Args:
            filepath_or_buffer: Path to the zip archive to be processed, or
                a buffer containing the zip archive to be processed in
                memory.
        """

        # open the zip archive
        archive = zipfile.ZipFile(filepath_or_buffer, 'r')
        
        # initaizlize DataFrame for holding the extracted data
        df = pd.DataFrame(columns=
            [
                'ct_id', 
                'title', 
                'status', 
                'principal_investigator', 
                'lead_sponsor', 
                'collaborators', 
                'estimated_completion_date'
            ]
        )
        
        # iterating through all files in the archive, we extract the wanted data
        for filename in archive.namelist():
            
            # open and read file contents into string
            file = archive.open(filename)
            file_as_string = file.read()
            
            # create XML tree
            root = ET.fromstring(file_as_string)
            
            # get all desired data
            
            # ct_id
            ct_id = root.find('id_info').find('nct_id').text

            # title
            title = root.find('official_title').text if root.find('official_title') is not None else root.find('brief_title').text if root.find('brief_title') is not None else None
            
            # status
            status = root.find('overall_status').text if root.find('overall_status') is not None else None
            
            # principal_investigator
            overall_official = root.find('overall_official')
            if overall_official:
                principal_investigator = overall_official.find('last_name').text
            
            # number_of_sites
            number_of_sites = len(root.findall('location'))

            # lead_sponsor
            lead_sponsor = root.find('sponsors').find('lead_sponsor').find('agency').text
            
            # collaborators
            collaborators = [collaborator.find('agency').text for collaborator in root.find('sponsors').findall('collaborator')]
            
            # estimated_completion_date
            estimated_completion_date = root.find('primary_completion_date').text if root.find('primary_completion_date') is not None else None

            # create row for insertion
            row = pd.Series({
                "ct_id": ct_id, 
                "title": title, 
                "status": status, 
                "principal_investigator": principal_investigator,
                "number_of_sites": number_of_sites, 
                "lead_sponsor": lead_sponsor, 
                "collaborators": collaborators,
                "estimated_completion_date": estimated_completion_date
            })

            # insert row into DataFrame
            df = df.append(row, ignore_index=True)
            
            # close the current file
            file.close()
            
        # close and delete the archive
        archive.close()
        
        # return the DataFrame for further processing
        return df
