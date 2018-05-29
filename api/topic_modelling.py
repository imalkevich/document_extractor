import argparse
import falcon
import os
import sys
import time
import threading

from falcon_cors import CORS
from waitress import serve

from knowledge_extractor.models import TopicModel
from extractor.loader import DocumentRawLoader

from . import __version__

MODEL_NOT_TRAINED = 'MODEL_NOT_TRAINED'
MODEL_TRAINING = 'MODEL_TRAINING'
MODEL_TRAINED = 'MODEL_TRAINED'

waitTime = int(os.environ.get('WAIT_TIME', '2'))

models = {}

def get_model_state(search_guid, topic_models):
    state = MODEL_NOT_TRAINED

    if search_guid in topic_models:
        state = MODEL_TRAINED if topic_models[search_guid].is_ready() else MODEL_TRAINING

    return state

class TopicModelApi(object):
    def on_post(self, request, response):
        search_guid = request.media.get('search_guid')
        state = get_model_state(search_guid, models)

        result = {
            'search_guid': search_guid,
            'state': state
        }

        if state == MODEL_NOT_TRAINED:
            documents = request.media.get('documents')
            model = TopicModel(search_guid, documents, analyze_full_doc=True)
            models[search_guid] = model
            def train_model():
                doc_guids = [doc['docGuid'] for doc in documents]
                DocumentRawLoader(doc_guids=doc_guids).load()
                model.train()

            threading.Thread(target=train_model).start()
            result['num_doc_guids'] = len(documents)
        elif state == MODEL_TRAINED:
            model = models[search_guid]
            
            result['documents'] = model.get_topic_profile()
            result['topics'] = model.get_top_words()

        response.media = result

class TopicModelStatusApi(object):
    def on_post(self, request, response):
        search_guid = request.media.get('search_guid')
        state = get_model_state(search_guid, models)

        result = {
            'search_guid': search_guid,
            'state': state
        }

        response.media = result

def get_parser():
    parser = argparse.ArgumentParser(description='load documents and extract text')

    parser.add_argument('-p', '--port', help='Port to listen requests', type=str)

    parser.add_argument('-v', '--version', help='displays the current version of topic modelling API',
                        action='store_true')

    return parser

def command_line_runner():
    parser = get_parser()
    _args = parser.parse_args()
    args = vars(_args)

    if args['version']:
        print(__version__)
        return

    if not args['port']:
        parser.print_help()
        return

    port = args['port']

    cors = CORS(allow_origins_list=[
                'https://1.next.demo.westlaw.com',
                'https://1.next.qed.westlaw.com',
                'http://10.143.24.72.ip.next.demo.westlaw.com'
            ],
            allow_all_headers=True,
            allow_all_methods=True)

    api = falcon.API(middleware=[cors.middleware])
    api.add_route('/topic_model', TopicModelApi())
    api.add_route('/topic_model_status', TopicModelStatusApi())

    serve(api, listen='*:{}'.format(port))

if __name__ == '__main__':
    command_line_runner()


