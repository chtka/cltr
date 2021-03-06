import lxml.etree
import pandas as pd
import zipfile

from processors.processor import Processor

class ANZCTRProcessor(Processor):
    """ 
    Processes the zip archives downloaded from the ANZCTR results
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
        
        # initialize DataFrame for holding the extracted data
        df = pd.DataFrame(columns=[
            'ct_id', 
            'title', 
            'status', 
            'principal_investigator', 
            'number_of_sites', 
            'lead_sponsor', 
            'collaborators', 
            'estimated_completion_date'
        ])
        
        # iterating through all files in the archive, we extract the wanted data
        for filename in [name for name in archive.namelist() 
            if name.endswith('.xml')]:
            
            # open and read file contents into string
            file = archive.open(filename)
            file_as_string = file.read()
            
            # create XML tree
            root = lxml.etree.fromstring(file_as_string)
            
            lxml.etree.fromstring(file_as_string)

            # get all desired data
            
            # actr_number/nct_id
            actr_number_list = root.xpath('./actrnumber/text()')
            
            if len(actr_number_list) == 0:
                ct_id = root.xpath('./nctid/text()')[0]
            else:
                ct_id = actr_number_list[0]
            
            # title
            title = root.xpath('./trial_identification/studytitle/text()')[0].strip()
            
            # status
            status = root.xpath('./stage/text()')[0].strip()
            
            # principal_investigator
            principal_investigator = root\
                .xpath(
                    './/type[text()="Principal Investigator"]/../name/text()'
                )[0].strip() if len(root.xpath(
                    './/type[text()="Principal Investigator"]/../name/text()'
                )) != 0 else None
            
            # number_of_sites - ANZCTR does not provide the number of sites
            number_of_sites = None
            
            # lead_sponsor
            lead_sponsor = root.xpath('.//primarysponsorname/text()')[0].strip()
            
            # collaborators - defined as all funding sources and collaborators (minus the primary sponsor)
            collaborators = list((set(root.xpath('.//fundingsource/fundingname/text()')) |
                                 set(root.xpath('.//othercollaborator/othercollaboratorname/text()'))) - {lead_sponsor})
            
            # estimated_completion_date - ANZCTR does not provide completion dates, only submission and approval dates
            estimated_completion_date = None
            
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
