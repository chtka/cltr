import sys
import io
import os
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import unittest

from processors.anzctr_processor import ANZCTRProcessor
from processors.clinical_trials_processor import ClinicalTrialsProcessor
from processors.isrctn_processor import ISRCTNProcessor

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
class TestProcessors(unittest.TestCase):

    def test_anzctr_processor(self):

        processor = ANZCTRProcessor()

        df = processor.process_and_load_df(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/anzctr_processor_test_data.zip'))

        trial = df.iloc[0]

        self.assertEqual(trial['ct_id'], "ACTRN12605000064606")
        self.assertEqual(trial['title'], "A randomised controlled trial of a simplified management strategy in OSA")
        self.assertEqual(trial['status'], "Registered")
        self.assertEqual(trial['principal_investigator'], None)
        self.assertEqual(trial['number_of_sites'], None)
        self.assertEqual(trial['lead_sponsor'], "NHMRC")
        self.assertEqual(set(trial['collaborators']), set(['Integneuro', 'RESMED']))
        self.assertEqual(trial['estimated_completion_date'], None)

    def test_clinical_trials_processor(self):
        
        processor = ClinicalTrialsProcessor()

        df = processor.process_and_load_df(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/clinical_trials_gov_processor_test_data.zip'))

        trial = df.iloc[0]

        self.assertEqual(trial['ct_id'], "NCT00251290")
        self.assertEqual(trial['title'], "Diagnosis and Treatment of Sleep-Disordered Breathing in the Homes of Patients With Transient Ischemic Attack")
        self.assertEqual(trial['status'], "Completed")
        self.assertEqual(trial['principal_investigator'], "Dawn M Bravata, MD")
        self.assertEqual(trial['lead_sponsor'], "Yale University")
        self.assertEqual(set(trial['collaborators']), set(['Robert Wood Johnson Foundation', 'ResMed Foundation', 'VA Office of Research and Development']))
        self.assertEqual(trial['estimated_completion_date'], "September 2007")
        self.assertEqual(trial['number_of_sites'], 3)

    def test_isrctn_processor(self):
        pass

