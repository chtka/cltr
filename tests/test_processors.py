import sys
import os
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import unittest

from processors.anzctr_processor import ANZCTRProcessor
from processors.clinical_trials_processor import ClinicalTrialsProcessor
from processors.isrctn_processor import ISRCTNProcessor

class TestProcessors(unittest.TestCase):

    def test_anzctr_processor(self):
        pass

    def test_clinical_trials_processor(self):
        pass

    def test_isrctn_processor(self):
        pass

