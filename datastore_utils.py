import os
from google.cloud import datastore


PROJECT_ID = os.environ.get('PROJECT_ID', 'ccblender')

def list_instances_of_word(word):
    client = datastore.Client(PROJECT_ID)
    query = client.query(kind='Captioned Word')
    query.add_filter('word', '=', word)
    word_instances = list(query.fetch())

    if len(word_instances) == 0:
        raise ValueError('No instances of that word were found')

    return word_instances
