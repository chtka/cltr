import os


from processors.isrctn_processor import ISRCTNProcessor
from processors.anzctr_processor import ANZCTRProcessor
from processors.clinical_trials_processor import ClinicalTrialsProcessor

from search_trials import CLINICAL_TRIALS_DATA_BUCKET_NAME

processor = ClinicalTrialsProcessor()

import boto3
import io

# buffer = io.BytesIO()

# s3 = boto3.resource('s3')

# obj = s3.Object(CLINICAL_TRIALS_DATA_BUCKET_NAME, 'ANZCTR/resmed/2018/06/26/anzctr_results_resmed.zip')
# obj.download_fileobj(buffer)

# df = processor.process_and_load_df(buffer)

# print(df.head())

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




