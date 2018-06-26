


from processors.isrctn_processor import ISRCTNProcessor

from search_trials import CLINICAL_TRIALS_DATA_BUCKET_NAME

processor = ISRCTNProcessor()

import boto3
import io

buffer = io.BytesIO()

s3 = boto3.resource('s3')

obj = s3.Object(CLINICAL_TRIALS_DATA_BUCKET_NAME, 'ISRCTN/resmed/2018/06/26/isrctn_results_resmed.parquet')
obj.download_fileobj(buffer)

df = processor.process_and_load_df(buffer)

print(df.head())
