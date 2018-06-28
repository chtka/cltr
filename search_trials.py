import boto3
import os
import datetime
import sys

from searchers.clinical_trials_searcher import ClinicalTrialsSearcher
from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.isrctn_searcher import ISRCTNSearcher

CLINICAL_TRIALS_DATA_BUCKET_NAME = "clinical-trials-analysis-data-raw"

CLINICAL_TRIALS_GOV_DATA_GLOBBING_PATTERN = CLINICAL_TRIALS_DATA_BUCKET_NAME + "/*/*/*/CLINICAL_TRIALS_GOV/*/*.zip"
ANZCTR_DATA_GLOBBING_PATTERN = CLINICAL_TRIALS_DATA_BUCKET_NAME + "/*/*/*/ANZCTR/*/*.zip"

RAW_DATA_FORMAT_STRING = "%d/%02d/%02d/%s/%s/%s"

def search_trials(terms, site_name, Searcher):
    with Searcher() as searcher:
        for term in terms:
            filepath = searcher.search_and_download_raw(term)
            if filepath:
                print("Downloaded", filepath)
                filepath_s3 = RAW_DATA_FORMAT_STRING % (d.year, d.month, d.day, site_name, term, filepath)
                bucket.upload_file(os.path.join(os.getcwd(), filepath), filepath_s3)
                os.remove(os.path.join(os.getcwd(), filepath))
                print("Uploaded", filepath_s3)
            else:
                print("No", site_name, "search results found for", term)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        search_terms_file_path = sys.argv[1]
    else:
        search_terms_file_path = "search_terms_short.txt"

    d = datetime.date.today()

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(CLINICAL_TRIALS_DATA_BUCKET_NAME)

    terms = []

    with open(search_terms_file_path) as f:
        while True:

            term = f.readline()

            if not term: 
                break

            terms.append(term.rstrip())

    search_trials(terms, "ANZCTR", ANZCTRSearcher)
    search_trials(terms, "CLINICAL_TRIALS_GOV", ClinicalTrialsSearcher)
