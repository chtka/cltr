import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


import boto3
import datetime
import io
import json
import logging
import os
from socket import gethostname
import sys

from searchers.clinical_trials_searcher import ClinicalTrialsSearcher
from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.isrctn_searcher import ISRCTNSearcher

RAW_DATA_FORMAT_STRING = "%d/%02d/%02d/%s/%s/%s"

def run_search_trials(config_path, no_upload=False):

    hostname = gethostname()

    # setting up logging
    log_buffer = io.StringIO()
    log_handler = logging.StreamHandler(log_buffer)
    logger = logging.getLogger("search_trials")
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

    print(hostname, "[%s]" % datetime.datetime.utcnow(), "START", __file__)    
    logger.info("%s [%s] START %s" % (hostname, datetime.datetime.utcnow(), __file__))

    searchers = dict()

    # config
    with open(config_path) as config_data_file:
        data = json.load(config_data_file)

        search_terms_file_path = data['search_terms_file_path']

        # config searchers
        for searcher_name in data['searchers']:
            if searcher_name == 'clinical-trials-gov':
                searchers['CLINICAL_TRIALS_GOV'] = ClinicalTrialsSearcher
            elif searcher_name == 'anzctr':
                searchers['ANZCTR'] = ANZCTRSearcher

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

    for searcher_name in searchers:

        with searchers[searcher_name]() as searcher:
            
            for term in terms:

                filepath = searcher.search_and_download_raw(term)
                if filepath:
                    print(hostname, "[%s]" % datetime.datetime.utcnow(), "DOWNLOAD", filepath)
                    logger.info("%s [%s] DOWNLOAD %s" % (hostname, datetime.datetime.utcnow(), filepath))


                    if not no_upload:
                        
                        filepath_s3 = RAW_DATA_FORMAT_STRING % (d.year, d.month, d.day, searcher_name, term, filepath)

                        bucket.upload_file(os.path.join(os.getcwd(), filepath), filepath_s3)

                        print(hostname, "[%s]" % datetime.datetime.utcnow(), "UPLOAD", filepath_s3)
                        logger.info("%s [%s] UPLOAD %s\n" % (hostname, datetime.datetime.utcnow(), filepath_s3))

                    os.remove(os.path.join(os.getcwd(), filepath))

                
                else:

                    print(hostname, "[%s]" % datetime.datetime.utcnow(),  "FAILED_SEARCH", searcher_name, "+", term)
                    logger.warning("%s [%s] FAILED_SEARCH: %s + %s" % (hostname, datetime.datetime.utcnow(), searcher_name, term))

    print(hostname, "[%s]" % datetime.datetime.utcnow(), "STOP", __file__)
    logger.info("%s [%s] STOP %s" % (hostname, datetime.datetime.utcnow(), __file__))

    if not no_upload:

        log_file_path = "%d/%02d/%02d/search_trials_%s.log" % (d.year, d.month, d.day, gethostname())

        s3.Object(data['bucket_names']['raw_data_bucket_name'], log_file_path).put(Body=log_buffer.getvalue())


if __name__ == "__main__":
    run_search_trials('config/config.json')
