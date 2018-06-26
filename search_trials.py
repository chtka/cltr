import boto3
import os
import datetime

from searchers.clinical_trials_searcher import ClinicalTrialsSearcher
from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.isrctn_searcher import ISRCTNSearcher


CLINICAL_TRIALS_DATA_BUCKET_NAME = "clinical-trials-analysis-data-raw"

if __name__ == "__main__":
    d = datetime.date.today()


    s3 = boto3.resource('s3')
    bucket = s3.Bucket(CLINICAL_TRIALS_DATA_BUCKET_NAME)

    # ctsearcher = ClinicalTrialsSearcher()
    # isrsearcher = ISRCTNSearcher()

    # isrctn_filepath = isrsearcher.search_and_download_raw("resmed")

    with ANZCTRSearcher() as anzsearcher:
        anzctr_filepath = anzsearcher.search_and_download_raw("resmed")
        anzctr_filepath_s3 = "%s/%s/%d/%02d/%02d/%s" % ("ANZCTR", "resmed", d.year, d.month, d.day, anzctr_filepath)
        bucket.upload_file(os.path.join(os.getcwd(), anzctr_filepath), anzctr_filepath_s3)
        os.remove(os.path.join(os.getcwd(), anzctr_filepath))

        anzctr_filepath = anzsearcher.search_and_download_raw("cpap")
        anzctr_filepath_s3 = "%s/%s/%d/%02d/%02d/%s" % ("ANZCTR", "cpap", d.year, d.month, d.day, anzctr_filepath)
        bucket.upload_file(os.path.join(os.getcwd(), anzctr_filepath), anzctr_filepath_s3)
        os.remove(os.path.join(os.getcwd(), anzctr_filepath))



    # isrctn_filepath_s3 = "%s/%s/%d/%02d/%02d/%s" % ("ISRCTN", "resmed", d.year, d.month, d.day, isrctn_filepath)

    # bucket.upload_file(os.path.join(os.getcwd(), isrctn_filepath), isrctn_filepath_s3)

    # os.remove(os.path.join(os.getcwd(), isrctn_filepath))

    # isrsearcher.close_browser()
    # ctsearcher.close_browser()
    # anzsearcher.close_browser()



    # // look into rss feeds, aws projects that already use them 