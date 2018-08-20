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

import collections

# parameters for RSS URL
UPDATE_LOG_S3_BUCKET = os.environ.get('ACTA_UPDATE_LOG_S3_BUCKET', 'acta-update-logs')
DAYS_AGO_UPDATED = os.environ.get('ACTA_DAYS_AGO_UPDATED', 30)
REC_COUNT = os.environ.get('RECT_COUNT', 10000)

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

terms = [
  'resmed'
]

for term in terms:
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
    resp = requests.get('http://localhost:9200/studies/_search', json={
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

        requests.put('http://localhost:9200/studies/_doc/%s' % nct_id, json=trial_dict)

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

      requests.put('http://localhost:9200/studies/_doc/%s' % nct_id, json=study2)

import boto3

s3 = boto3.client('s3')


s3.put_object(Body=str.encode(json.dumps(log)), Bucket=UPDATE_LOG_S3_BUCKET, Key=str(log['process_started']) + '.json')