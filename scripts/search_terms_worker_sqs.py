import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import boto3
import datetime
from socket import gethostname
import json
import os
from time import sleep

from searchers.isrctn_searcher import ISRCTNSearcher
from searchers.anzctr_searcher import ANZCTRSearcher
from searchers.clinical_trials_searcher import ClinicalTrialsSearcher

hostname = gethostname()

CLINICAL_TRIALS_SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

RAW_DATA_S3_BUCKET = os.environ['RAW_DATA_S3_BUCKET']

AWS_REGION = os.environ['AWS_REGION']

print(CLINICAL_TRIALS_SQS_QUEUE_URL, RAW_DATA_S3_BUCKET)

print('Connecting to AWS resources...')

sqs = boto3.client('sqs', region_name=AWS_REGION)
s3 = boto3.resource('s3', region_name=AWS_REGION)

bucket = s3.Bucket(RAW_DATA_S3_BUCKET)

RAW_DATA_FORMAT_STRING = "%d/%02d/%02d/%s/%s/%s"

d = datetime.date.today()

response = sqs.receive_message(
    QueueUrl=CLINICAL_TRIALS_SQS_QUEUE_URL,
    AttributeNames=[
        'SentTimestamp'
    ],
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ],
    VisibilityTimeout=1800,
    WaitTimeSeconds=0
)

print(response)

try:

    cltr_searcher = ClinicalTrialsSearcher()
    
    while response.get('Messages', None):
        
        message = response['Messages'][0]

        search_term = message['MessageAttributes']['search-term']['StringValue']

        print(search_term)

        filepath = cltr_searcher.search_and_download_raw(search_term)
        if filepath:
            print(hostname, '[%s]' % datetime.datetime.utcnow(), "DOWNLOAD", filepath)

            # upload file and remove local copy
            filepath_s3 = RAW_DATA_FORMAT_STRING % (d.year, d.month, d.day, 'CLINICAL_TRIALS_GOV', search_term, filepath)
            bucket.upload_file(os.path.join(os.getcwd(), filepath), filepath_s3)
            os.remove(os.path.join(os.getcwd(), filepath))
            
            print(hostname, "[%s]" % datetime.datetime.utcnow(), "UPLOAD", filepath_s3)

        sqs.delete_message(
            QueueUrl=CLINICAL_TRIALS_SQS_QUEUE_URL,
            ReceiptHandle=message['ReceiptHandle']
        )

        response = sqs.receive_message(
            QueueUrl=CLINICAL_TRIALS_SQS_QUEUE_URL,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=1800,
            WaitTimeSeconds=0
        )
finally:

    cltr_searcher.close_browser()

    if path.exists(os.path.join(os.getcwd(), filepath)):
        os.remove(os.path.join(os.getcwd(), filepath))
