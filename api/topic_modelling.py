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

waitTime = int(os.environ.get('WAIT_TIME', '2'))

models = {}

class TopicModelApi(object):
    def on_post(self, request, response):
        search_guid = request.media.get('search_guid')

        result = {'search_guid': search_guid}

        if search_guid not in models:
            doc_guids = list(set(request.media.get('doc_guids')))
            model = TopicModel(search_guid, doc_guids)
            models[search_guid] = model
            def train_model():
                DocumentRawLoader(doc_guids=doc_guids).load()
                model.train()

            threading.Thread(target=train_model).start()
            result['num_doc_guids'] = len(doc_guids)
            result['state'] = 'MODEL_TRAINING_STARTED'
        else:
            model = models[search_guid]
            if model.is_ready():
                documents = model.get_topic_profile()

                result['documents'] = documents
                result['state'] = 'MODEL_TRAINED'
            else:
                result['state'] = 'MODEL_TRAINING'

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
                'https://1.next.qed.westlaw.com'
            ],
            allow_all_headers=True,
            allow_all_methods=True)

    api = falcon.API(middleware=[cors.middleware])
    api.add_route('/topic_model', TopicModelApi())

    serve(api, listen='*:{}'.format(port))

if __name__ == '__main__':
    command_line_runner()


