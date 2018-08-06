import os
print(os.environ.get('SQS_QUEUE_URL', None))
print(os.environ.get('RAW_DATA_S3_BUCKET', None))