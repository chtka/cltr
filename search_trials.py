import boto3
import datetime
import io
import json
import os
import sys

from searchers.clinical_trials_searcher import ClinicalTrialsSearcher
from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.isrctn_searcher import ISRCTNSearcher



RAW_DATA_FORMAT_STRING = "%d/%02d/%02d/%s/%s/%s"

def search_trials(terms, site_name, Searcher, log_buffer):
    """
    Uses the specified Searcher to query the given site using the list of
    query terms. Downloads the raw data and uploads it to S3.

    Args:
        terms: The list of terms to search for.
        site_name: The website/database being searched.
        Searcher: The type of searcher to use for searching.

    Returns:
        None.
    """
    with Searcher() as searcher:
        for term in terms:

            # download the raw data
            filepath = searcher.search_and_download_raw(term)
            if filepath:
                
                print("[%s]" % datetime.datetime.utcnow(), "DOWNLOAD", filepath)
                log_buffer.write("[%s] DOWNLOAD %s\n" % (datetime.datetime.utcnow(), filepath))
                
                # upload file and remove local copy
                filepath_s3 = RAW_DATA_FORMAT_STRING % (d.year, d.month, d.day, site_name, term, filepath)
                bucket.upload_file(os.path.join(os.getcwd(), filepath), filepath_s3)
                os.remove(os.path.join(os.getcwd(), filepath))
                
                print("[%s]" % datetime.datetime.utcnow(), "UPLOAD", filepath_s3)
                log_buffer.write("[%s] UPLOAD %s\n" % (datetime.datetime.utcnow(), filepath_s3))
            
            else:

                print("[%s]" % datetime.datetime.utcnow(),  "FAILED_SEARCH", site_name, "+", term)
                log_buffer.write("[%s] FAILED_SEARCH: %s + %s\n" % (datetime.datetime.utcnow(), site_name, term))

if __name__ == "__main__":

    log_buffer = io.StringIO()

    print("[%s]" % datetime.datetime.utcnow(), "START", __file__)    
    log_buffer.write("[%s] START %s\n" % (datetime.datetime.utcnow(), __file__))

    searchers = []

    # config
    with open('config.json') as config_data_file:
        data = json.load(config_data_file)

        search_terms_file_path = data['search_terms_file_path']

        # config searchers
        for searcher_name in data['searchers']:
            if searcher_name == 'clinical-trials-gov':
                searchers.append(ClinicalTrialsSearcher)
            elif searcher_name == 'anzctr':
                searchers.append(ANZCTRSearcher)

    d = datetime.date.today()

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(data['bucket_names']['raw_data_bucket_name'])

    terms = []

    with open(search_terms_file_path) as f:
        while True:

            term = f.readline()

            if not term: 
                break

            terms.append(term.rstrip())


    search_trials(terms, "ANZCTR", ANZCTRSearcher, log_buffer)
    search_trials(terms, "CLINICAL_TRIALS_GOV", ClinicalTrialsSearcher, log_buffer)

    
    print("[%s]" % datetime.datetime.utcnow(), "STOP", __file__)
    log_buffer.write("[%s] STOP %s\n" % (datetime.datetime.utcnow(), __file__))

    log_file_path = "%d/%02d/%02d/search_trials.log" % (d.year, d.month, d.day)

    s3.Object(data['bucket_names']['raw_data_bucket_name'], log_file_path).put(Body=log_buffer.getvalue())

