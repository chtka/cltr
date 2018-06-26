import pandas as pd

from processors.processor import Processor

class ISRCTNProcessor(Processor):
    def process_and_load_df(self, filepath):

        # utility function for converting the downloaded CSV data
        def strip_str_list_els(els):
            return list(map(str.strip, els))

        df = pd.read_parquet(filepath)

        # rename our desired columns
        df = df.rename(
            index=str, 
            columns={
                'Sponsor': 'lead_sponsor',
                'Overall trial end': 'estimated_completion_date',
                'ISRCTN': 'ct_id', 'Overall trial status': 'status',
                'Title': 'title'
            }
        )
        
        # collaborators defined as all funders, except for lead_sponsor
        df['collaborators'] = (df['Funder'].str.split(';')\
            .apply(strip_str_list_els).apply(set) 
                - df['lead_sponsor'].apply(lambda s: {s})).apply(list)

        df = df[[
            'ct_id', 
            'title', 
            'status', 
            'principal_investigator', 
            'number_of_sites', 
            'lead_sponsor', 
            'collaborators', 
            'estimated_completion_date'
        ]]

        return df