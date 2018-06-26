


from processors.isrctn_processor import ISRCTNProcessor
from processors.anzctr_processor import ANZCTRProcessor
from processors.clinical_trials_processor import ClinicalTrialsProcessor

from search_trials import CLINICAL_TRIALS_DATA_BUCKET_NAME

processor = ANZCTRProcessor()

import boto3
import io

buffer = io.BytesIO()

s3 = boto3.resource('s3')

obj = s3.Object(CLINICAL_TRIALS_DATA_BUCKET_NAME, 'ANZCTR/resmed/2018/06/26/anzctr_results_resmed.zip')
obj.download_fileobj(buffer)

df = processor.process_and_load_df(buffer)

print(df.head())

