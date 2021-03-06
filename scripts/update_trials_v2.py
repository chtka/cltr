import boto3
import os
import xmltodict

from lxml import etree
from os import path
from urllib.request import urlretrieve, urlopen
from urllib.parse import urlencode

# boto3 config.
AWS_REGION = os.environ['ACTA_AWS_REGION']

# ClinicalTrials.gov URLs
RSS_BASE_URL = 'https://clinicaltrials.gov/ct2/results/rss.xml?'
TRIAL_XML_BASE_URL = 'https://clinicaltrials.gov/ct2/show/%s?displayxml=true'

# AWS resources config
RAW_XML_S3_BUCKET = os.environ['ACTA_RAW_XML_S3_BUCKET']
XML_DATA_PREFIX = os.environ.get('ACTA_XML_DATA_PREFIX', '')
UPDATE_TRIALS_SQS_QUEUE_URL = os.environ['ACTA_UPDATE_TRIALS_SQS_QUEUE_URL']

def clear_xml_attribs(root):
    root.attrib.clear()
    tree_itr = root.getiterator()
    for el in tree_itr:
        el.attrib.clear()

s3 = boto3.client('s3')
sqs = boto3.client('sqs', region_name=AWS_REGION)

response = sqs.receive_message(
    QueueUrl=UPDATE_TRIALS_SQS_QUEUE_URL,
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

while response.get('Messages', None):

    message = response['Messages'][0]
    term = message['MessageAttributes']['search-term']['StringValue']
    print('START TRIAL UPDATES - %s' % term)

    with urlopen(RSS_BASE_URL + urlencode({
        'lup_d': 30,
        'term': term,
        'count': 10000
    })) as resp:
        root = etree.fromstring(resp.read())
        clear_xml_attribs(root)
        rss_dict = xmltodict.parse(etree.tostring(root))
        ids = [item['guid'] for item in rss_dict['rss']['channel'].get('item', [])]
        for nct_id in ids:
            print('UPLOAD %s.xml', nct_id)
            with urlopen(TRIAL_XML_BASE_URL % nct_id) as trial_xml_resp:
                root = etree.fromstring(trial_xml_resp.read())
                clear_xml_attribs(root)
                s3.put_object(Body=etree.tostring(root), Bucket=RAW_XML_S3_BUCKET, Key=path.join(XML_DATA_PREFIX, '%s.xml' % nct_id))

    
    sqs.delete_message(
        QueueUrl=UPDATE_TRIALS_SQS_QUEUE_URL,
        ReceiptHandle=message['ReceiptHandle']
    )

    print('END TRIAL UPDATES - %s' % term)
    response = sqs.receive_message(
        QueueUrl=UPDATE_TRIALS_SQS_QUEUE_URL,
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

