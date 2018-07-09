import boto3
import datetime
from socket import gethostname
import json
import os

hostname = gethostname()

CLINICAL_TRIALS_SQS_QUEUE_URL = os.environ.get('CLINICAL_TRIALS_SQS_QUEUE_URL', 
    'https://sqs.us-west-1.amazonaws.com/274059113391/AutomatedClinicalTrialsAnalysis')

print(hostname, "[%s]" % datetime.datetime.utcnow(), "START", __file__)    

with open('config.json') as config_data_file:
    data = json.load(config_data_file)

    search_terms_file_path = data['search_terms_file_path']

terms = []

with open(search_terms_file_path) as f:
    while True:

        term = f.readline()

        if not term: 
            break

        terms.append(term.rstrip())

sqs = boto3.client('sqs')

                # print(hostname, "[%s]" % datetime.datetime.utcnow(), "DOWNLOAD", filepath)

for term in terms:

    print(hostname, '[%s]' % datetime.datetime.utcnow(), 'SEND MESSAGE \'%s\' to search term queue' % term)

    sqs.send_message(
        QueueUrl=CLINICAL_TRIALS_SQS_QUEUE_URL,
        MessageBody='Search term information',
        MessageAttributes={
            'search-term': {
                'DataType': 'String',
                'StringValue': term
            }
        }
    )

print(hostname, "[%s]" % datetime.datetime.utcnow(), "STOP", __file__)    







