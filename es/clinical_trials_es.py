import json

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


    