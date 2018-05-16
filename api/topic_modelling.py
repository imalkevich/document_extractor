import argparse
import falcon
import os
import time

from falcon_cors import CORS
from waitress import serve

from knowledge_extractor.models import TopicModel

from . import __version__

waitTime = int(os.environ.get('WAIT_TIME', '2'))

class TopicModelApi(object):
    def on_post(self, request, response):
        doc_guids = request.media.get('doc_guids')

        result = {'num_doc_guids': len(doc_guids)}
        response.media = result

def get_parser():
    parser = argparse.ArgumentParser(description='load documents and extract text')

    parser.add_argument('-p', '--port', help='Port to listen requests', type=str)

    parser.add_argument('-v', '--version', help='displays the current version of topic modelling API',
                        action='store_true')

    return parser

def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if not args['port']:
        parser.print_help()
        return

    port = args['port']

    cors = CORS(allow_origins_list=[
                'https://1.next.qed.westlaw.com'
            ],
            allow_all_headers=True,
            allow_all_methods=True)

    api = falcon.API(middleware=[cors.middleware])
    api.add_route('/topic_model', TopicModelApi())

    serve(api, listen='*:{}'.format(port))

if __name__ == '__main__':
    command_line_runner()


