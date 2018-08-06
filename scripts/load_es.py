import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


import json
import s3fs

from elasticsearch import Elasticsearch, helpers

def get_bulk_api_formatted_generator(fs_open, path, _index, _type):

    with fs_open(path) as data:
        for entry in data:
            action = {
                '_index': _index,
                '_type': _type,
                '_source': json.loads(entry)
            }

            yield action

def load_es(**config):

    # config

    es = Elasticsearch(config['elasticsearch_endpoint'])
    fs = s3fs.S3FileSystem()

    gen = get_bulk_api_formatted_generator(fs.open, 
        'ct-analysis-data-postprocessing/clinical_trials_all.json', 
        'ct2',
        'doc'
    )

    helpers.bulk(es, gen)

if __name__ == '__main__':

    with open('config/config.json') as f:
        config = json.load(f)

    load_es(**config)


    