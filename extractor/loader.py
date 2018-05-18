"""
Loader module.
"""

import argparse
import inspect
import os
import random
import re
import requests
import sys

import xml.etree.ElementTree as ET

from . import __version__
from datetime import datetime

re_clean = re.compile('<.*?>')

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
                'Safari/536.5'), )

URL = 'http://document.int.next.qed.westlaw.com/document/v1/rawxml/{}?websitehost=next.qed.westlaw.com'

def print_now(message, timestamp = True):
    if timestamp:
        message = '{}    {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'), message)
    print(message)
    sys.stdout.flush()

class DocumentRawLoader(object):
    def __init__(self, doc_guids_file=None, doc_guids=None):
        self.doc_guids_file = doc_guids_file
        self.doc_guids = doc_guids

    def load(self):
        doc_guids = self.doc_guids if self.doc_guids is not None else self._get_doc_guids()
        counter = 0
        start_all = datetime.now()
        for guid in doc_guids:
            try:
                if os.path.isfile(self._get_file_name(guid)):
                    print_now('{} is already loaded'.format(guid))
                    continue

                start = datetime.now()
                doc_xml = self._load_doc_by_guid(guid)
                lines = self._extract_text_from_xml(doc_xml)
                self._save_text(guid, lines)
                print_now('{} loading took {}'.format(guid, (datetime.now() - start)))
                counter += 1
            except:
                print_now('Failed to load doc with guid: {}, error: {}'.format(guid, sys.exc_info()))
        
        print_now('{} documents loaded in {}'.format(counter, (datetime.now() - start_all)))

    def _load_doc_by_guid(self, guid):
        session = requests.session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        response = session.get(
            URL.format(guid), 
            headers={ 'User-Agent': random.choice(USER_AGENTS) }
        ).text

        session.close()
        return response

    def _extract_text_from_xml(self, xml):
        tree = ET.fromstring(xml)
        nodes = tree.findall('.//paratext')
        result = []
        for n in nodes:
            paragraph = []
            for child in n.getchildren():
                res = ET.tostring(child, encoding='unicode')
                res = re.sub(re_clean, ' ', res)
                res = res.replace('“', '').replace('”', '') \
                        .replace('', '')

                for line in res.split('\n'):
                    line = line.strip()
                    if len(line) > 0 and line.isdigit() == False:
                        paragraph.append(line)
            
            text = ' '.join(paragraph).strip()
            
            if len(text) > 0:
                result.append(text)

        return result

    def _save_text(self, guid, lines):
        file_name = self._get_file_name(guid)

        with open(file_name, 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(line + '\n')

    def _get_file_name(self, guid):
        parent_path = os.path.dirname(os.path.dirname(inspect.getfile(self.__class__)))
        dir_path = os.path.join(
            parent_path,
            'documents')

        if not os.path.isdir(dir_path):
             os.makedirs(dir_path)

        file_name = os.path.join(
            dir_path,
            '{}.txt'.format(guid)
        )

        return file_name

    def _get_doc_guids(self):
        doc_guids = []
        with open(self.doc_guids_file, 'r') as file:
            for line in file:
                for guid in self._get_doc_guids_from_line(line):
                    doc_guids.append(guid)

        return doc_guids

    def _get_doc_guids_from_line(self, line):
        guids = [guid.strip().replace('"', '') for guid in line.split(',') if len(line.strip()) > 0]

        return guids



def get_parser():
    parser = argparse.ArgumentParser(description='load documents and extract text')

    parser.add_argument('-f', '--file', help='file with document guids', type=str)

    parser.add_argument('-v', '--version', help='displays the current version of errorguimonitor',
                        action='store_true')

    return parser

def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if not args['file']:
        parser.print_help()
        return

    file = args['file']

    if not os.path.isfile(file):
        print('{} does not exist'.format(file))
        parser.print_help()
        return

    loader = DocumentRawLoader(file)
    loader.load()

if __name__ == '__main__':
    command_line_runner()