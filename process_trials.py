import os


from processors.isrctn_processor import ISRCTNProcessor
from processors.anzctr_processor import ANZCTRProcessor
from processors.clinical_trials_processor import ClinicalTrialsProcessor

from search_trials import CLINICAL_TRIALS_DATA_BUCKET_NAME

CLINICAL_TRIALS_PROCESSED_DATA_BUCKET_NAME = 'clinical-trials-analysis-data-postprocessing'

processor = ClinicalTrialsProcessor()

import boto3
import io

s3 = boto3.resource('s3')
bucket = s3.Bucket(CLINICAL_TRIALS_DATA_BUCKET_NAME)

for obj_summary in bucket.objects.all():
    buffer = io.BytesIO()
    obj = obj_summary.Object()

    print('Processing %s' % obj.key)

    obj.download_fileobj(buffer)

    df = processor.process_and_load_df(buffer)

    csv_buffer = io.StringIO()

    df.to_csv(csv_buffer)

    s3.Object('clinical-trials-analysis-data-postprocessing', os.path.splitext(obj_summary.key)[0] + '.csv').put(Body=csv_buffer.getvalue())




