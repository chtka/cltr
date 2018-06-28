import datetime
import io
import json
import os
import s3fs

from processors.isrctn_processor import ISRCTNProcessor
from processors.anzctr_processor import ANZCTRProcessor
from processors.clinical_trials_processor import ClinicalTrialsProcessor

def process_trials(fsys, paths, bucket, processor):
    """
    Processes the specified file data paths using the provided processor type
    and uploads the data to the desired S3 bucket.

    Args:
        fsys: The filesystem containing the files specified in the "paths"
        argument.
        
        paths: A list of the paths of the files to be processed.
        
        bucket: The S3 bucket to which the processed data will be uploaded.
        
        processor: The class of the processor to use for processing the
        specified data.
    
    Returns:
        None
    """

    for path in paths:
        with fsys.open(path) as data:

            print("[%s]" % datetime.datetime.utcnow(), "DOWNLOAD", path)

            # use the processor to load the raw data into pandas
            # DataFrame and transform it as desired
            df = processor.process_and_load_df(data)

            # getting the output file path
            [_, obj] = path.split('/', 1)
            outfile_path = bucket + '/' + os.path.splitext(obj)[0] + '.json'

            # write the file to S3 in JSON format
            with fsys.open(outfile_path, 'wb') as f:
                f.write(str.encode(df.to_json(orient='records', lines=True)))
                f.flush()

            print("[%s]" % datetime.datetime.utcnow(), "UPLOAD", outfile_path)

if __name__ == '__main__':

    print("[%s]" % datetime.datetime.utcnow(), "START", __file__)

    # config
    with open('config.json') as config_data_file:
        data = json.load(config_data_file)

    CLINICAL_TRIALS_RAW_DATA_BUCKET_NAME = data['bucket_names']['raw_data_bucket_name']
    CLINICAL_TRIALS_PROCESSED_DATA_BUCKET_NAME = data['bucket_names']['processed_data_bucket_name']

    CLINICAL_TRIALS_GOV_DATA_GLOBBING_PATTERN = CLINICAL_TRIALS_RAW_DATA_BUCKET_NAME + "/*/*/*/CLINICAL_TRIALS_GOV/*/*.zip"
    ANZCTR_DATA_GLOBBING_PATTERN = CLINICAL_TRIALS_RAW_DATA_BUCKET_NAME + "/*/*/*/ANZCTR/*/*.zip"
        

    # using s3fs to access our S3 buckets like a local filesystem
    fs = s3fs.S3FileSystem()

    # process ClinicalTrials.gov data
    clinical_trials_gov_paths = fs.glob(CLINICAL_TRIALS_GOV_DATA_GLOBBING_PATTERN)
    process_trials(fs, clinical_trials_gov_paths, CLINICAL_TRIALS_PROCESSED_DATA_BUCKET_NAME, ClinicalTrialsProcessor())

    # process ANZCTR database data
    anzctr_trials_paths = fs.glob(ANZCTR_DATA_GLOBBING_PATTERN)
    process_trials(fs, anzctr_trials_paths, CLINICAL_TRIALS_PROCESSED_DATA_BUCKET_NAME, ANZCTRProcessor())

    print("[%s]" % datetime.datetime.utcnow(), "STOP", __file__)

