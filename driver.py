import sys
import time
timestr = time.strftime("%Y%m%d-%H%M%S")

from searchers.clinical_trials_searcher import ClinicalTrialsSearcher

file_path = sys.argv[1]

with open(file_path) as f:
  while True:

    term = f.readline()

    if not term: 
      break

    term = term.rstrip()

    

    


