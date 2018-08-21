import os
import json
from lxml import etree
import xmltodict
import zipfile
from io import BytesIO
from urllib.request import urlretrieve, urlopen
from urllib.parse import urlencode
from elasticsearch import Elasticsearch, helpers
import requests
import time
import jsondiff
import json
import boto3

import collections

AWS_REGION = os.environ.get('AWS_REGION', 'us-west-1')
UPDATE_TRIALS_SQS_QUEUE_URL = os.environ.get('ACTA_UPDATE_TRIALS_SQS_QUEUE_URL', 'https://sqs.us-west-1.amazonaws.com/274059113391/SQS-Test')
AWS_ELASTICSEARCH_ENDPOINT = os.environ.get('ACTA_AWS_ELASTICSEARCH_ENDPOINT', 'http://localhost:9200')

AWS_ELASTICSEARCH_ENDPOINT = 'https://search-acta-lqudfuj44ynzcdjrsjektaz4lq.us-west-1.es.amazonaws.com'

# parameters for RSS URL
UPDATE_LOG_S3_BUCKET = os.environ.get('ACTA_UPDATE_LOG_S3_BUCKET', 'acta-update-logs')
DAYS_AGO_UPDATED = os.environ.get('ACTA_DAYS_AGO_UPDATED', 30)
REC_COUNT = os.environ.get('ACTA_REC_COUNT', 10000)

# Base URLs for downloading clinical trial data
RSS_BASE_URL = 'https://clinicaltrials.gov/ct2/results/rss.xml?'
TRIAL_XML_BASE_URL = 'https://clinicaltrials.gov/ct2/show/%s?displayxml=true'

def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def clear_xml_attribs(root):
  root.attrib.clear()
  tree_itr = root.getiterator()
  for el in tree_itr:
    el.attrib.clear()

log = {
  'created': dict(),
  'updated': dict(),
  'process_started': int(time.time()) 
}

sqs = boto3.client('sqs', region_name=AWS_REGION)

print('Checking for terms...')

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

  print('checking for updates for studies matching term: %s' % term)

  with urlopen(RSS_BASE_URL + urlencode({
    'lup_d': DAYS_AGO_UPDATED,
    'term': term,
    'count': REC_COUNT
  })) as resp:

    root = etree.fromstring(resp.read())
    clear_xml_attribs(root)
    rss_dict = xmltodict.parse(etree.tostring(root))
  
  ids = [item['guid'] for item in rss_dict['rss']['channel'].get('item', [])]

  for nct_id in ids:
    print('Checking if %s is a new trial...' % nct_id)
    resp = requests.get(AWS_ELASTICSEARCH_ENDPOINT + '/studies/_search', json={
        'query': {
            'match': {
                'id_info.nct_id': nct_id
            }
        }
    })

    resp_json = resp.json()

    if resp_json['hits']['total'] == 0:

      print('Inserting study %s...' % nct_id)

      with urlopen(TRIAL_XML_BASE_URL % nct_id) as trial_xml_resp:
        root = etree.fromstring(trial_xml_resp.read())
        clear_xml_attribs(root)
        trial_dict = xmltodict.parse(etree.tostring(root))
        trial_dict = trial_dict['clinical_study']
        trial_dict.pop('required_header')    
        trial_dict['timestamp'] = int(time.time())

        requests.put(AWS_ELASTICSEARCH_ENDPOINT + '/studies/_doc/%s' % nct_id, json=trial_dict)

        log['created'][nct_id] = {
          'source': trial_dict
        }    

      continue

    print('Study %s exists in Elasticsearch index.' % nct_id)

    study = resp_json['hits']['hits'][0]['_source']
    study.pop('timestamp')
    
    with urlopen(TRIAL_XML_BASE_URL % nct_id) as resp:
      root = etree.fromstring(resp.read())
      clear_xml_attribs(root)
      record_dict = xmltodict.parse(etree.tostring(root))
      study2 = record_dict['clinical_study']
      study2.pop('required_header')
        

    if study == study2:
      print('No differences found in %s.' % nct_id)
    else:
      diff = jsondiff.diff(flatten(study), flatten(study2), syntax='symmetric')
      log['updated'][nct_id] = dict()

      for k, v in diff.items():
        if k == jsondiff.insert:
          for k1, v1 in v.items():
            log['updated'][nct_id][k1] = {
              'prev_val': None,
              'new_val': v1
            }
        elif k == jsondiff.delete:
          for k1, v1 in v.items():
            log['updated'][nct_id][k1] = {
              'prev_val': v1,
              'new_val': None
            }
        else:
          log['updated'][nct_id][k] = {
            'prev_val': v[0],
            'curr_val': v[1]
          }
      study2['timestamp'] = int(time.time())

      requests.put(AWS_ELASTICSEARCH_ENDPOINT + '/studies/_doc/%s' % nct_id, json=study2)

  sqs.delete_message(
    QueueUrl=UPDATE_TRIALS_SQS_QUEUE_URL,
    ReceiptHandle=message['ReceiptHandle']
  )

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
s3 = boto3.client('s3', region_name=AWS_REGION)


s3.put_object(Body=str.encode(json.dumps(log)), Bucket=UPDATE_LOG_S3_BUCKET, Key=str(log['process_started']) + '.json')