import boto3
import os
import datetime
import sys

from searchers.clinical_trials_searcher import ClinicalTrialsSearcher
from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.isrctn_searcher import ISRCTNSearcher

CLINICAL_TRIALS_DATA_BUCKET_NAME = "clinical-trials-analysis-data-raw"

RAW_DATA_FORMAT_STRING = "%d/%02d/%02d/%s/%s/%s"

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

    with ANZCTRSearcher() as anzsearcher:

        for term in terms:

            anzctr_filepath = anzsearcher.search_and_download_raw(term)
            if anzctr_filepath:
                print("Downloaded", anzctr_filepath)
                anzctr_filepath_s3 = RAW_DATA_FORMAT_STRING % (d.year, d.month, d.day, "ANZCTR", term, anzctr_filepath)
                bucket.upload_file(os.path.join(os.getcwd(), anzctr_filepath), anzctr_filepath_s3)
                os.remove(os.path.join(os.getcwd(), anzctr_filepath))
                print("Uploaded", anzctr_filepath_s3)
            else:
                print("No ANZCTR search results found for", term)

    # with ISRCTNSearcher() as isrsearcher:

    #     for term in terms:

    #         isrctn_filepath = isrsearcher.search_and_download_raw(term)

    #         print(isrctn_filepath)

    #         if isrctn_filepath:
    #             isrctn_filepath_s3 = "%s/%s/%d/%02d/%02d/%s" % ("ISRCTN", term, d.year, d.month, d.day, isrctn_filepath)
    #             bucket.upload_file(os.path.join(os.getcwd(), isrctn_filepath), isrctn_filepath_s3)
    #             os.remove(os.path.join(os.getcwd(), isrctn_filepath))

    with ClinicalTrialsSearcher() as cltrsearcher:

        for term in terms:

            cltr_filepath = cltrsearcher.search_and_download_raw(term)

            print(cltr_filepath)

            if cltr_filepath:
                print("Downloaded", cltr_filepath, ".")
                cltr_filepath_s3 = RAW_DATA_FORMAT_STRING % (d.year, d.month, d.day, "CLINICAL_TRIALS_GOV", term, cltr_filepath)
                bucket.upload_file(os.path.join(os.getcwd(), cltr_filepath), cltr_filepath_s3)
                os.remove(os.path.join(os.getcwd(), cltr_filepath))    
                print("Uploaded", cltr_filepath_s3, ".")
            else:
                print("No ClinicalTrials.gov search results found for", term, ".")