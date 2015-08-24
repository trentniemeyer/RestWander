from flask import Flask

import os
from collections import defaultdict
import nltk
from nltk.tokenize import RegexpTokenizer

from elasticsearch import Elasticsearch
import Snippets
import json

app = Flask(__name__)
frequency = None
tokenizer = None
client = None

def initialize ():

    global frequency, tokenizer, client
    frequency = defaultdict(int)
    with open(os.path.expanduser('~/Downloads/positive-words.txt'), 'r') as f:
        for line in f:
            if line.startswith(';') == False:
                l = line.strip()
                frequency[l] = l

    tokenizer = RegexpTokenizer(r'\w+')
    client = Elasticsearch('localhost')

def filterpositives (seq):
    for tuple in seq:
        if len(tuple[1]) > 1 or "!" in tuple[0]: yield tuple[0]


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/positivestatements/<id>')
@Snippets.crossdomain(origin='*')
def positivestatements(id):


    response = client.search (index="blogs",
        body={
            "size": 1,
            "query": {
                "match": {
                  "_id": id
                }
            },
            "fields":"body"
        })

    if (len(response['hits']['hits']) == 1):

        text = str(response['hits']['hits'][0]['fields']['body']).replace (u'\\xa0', ' ').replace(u'\\n', '')

        sentences = nltk.sent_tokenize(text.lower())

        positivesentences = []
        for sentence in sentences:
            if len (sentence) > 300:
                continue
            tokens = tokenizer.tokenize(sentence)
            positives = []
            for token in tokens:
               if frequency.has_key(token):
                positives.append(token)

            if len(positives) > 0:
                positivesentences.append((sentence, positives))


        ratio = len(positivesentences) * 1.0 / (len(sentences) * 1.0)

        if ratio > 0.333:
            return json.dumps(list(filterpositives(positivesentences)))
        else:
            return json.dumps([tuple[0] for tuple in positivesentences])
    else:
        return "Id Not Found"

if __name__ == '__main__':
    initialize()
    app.run(debug=True)

