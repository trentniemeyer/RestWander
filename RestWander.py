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

def initialize ():

    global frequency, tokenizer, client
    frequency = defaultdict(int)
    with open(os.path.expanduser('~/Downloads/positive-words.txt'), 'r') as f:
        for line in f:
            if line.startswith(';') == False:
                l = line.strip()
                frequency[l] = l

    tokenizer = RegexpTokenizer(r'\w+')

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/positivestatements/<id>')
@Snippets.crossdomain(origin='*')
def positivestatements(id):

    client = Elasticsearch('http://137.135.93.224:9200')

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

        text = unicode(response['hits']['hits'][0]['fields']['body'][0])

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

            if (sentence.endswith('!')):
                positives.append('!')

            if len(positives) > 0:
                positivesentences.append((sentence, positives))

        positivesentences = sorted(positivesentences, key=lambda t: len(t[0]) * -1 * len (t[1]))

        return json.dumps([tuple[0] for tuple in positivesentences] [0:5], ensure_ascii=False, encoding='utf16')
    else:
        return "Id Not Found"

if __name__ == '__main__':
    initialize()
    app.run(debug=True)

