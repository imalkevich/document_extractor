"""
Loader module.
"""

import random
import requests

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
                'Safari/536.5'), )

URL = 'http://document.int.next.qed.westlaw.com/document/v1/rawxml/{}?websitehost=next.qed.westlaw.com'

class DocumentRawLoader(object):
    def __init__(self, doc_guids):
        self.doc_guids = doc_guids

    def load(self):
        for guid in self.doc_guids:
            try:
                doc_xml = self._load_doc_by_guid(guid)
            except:
                print('Failed to load doc with guid: {}'.format(guid))

    def _load_doc_by_guid(self, guid):
        session = requests.session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        response = session.get(
            URL.format(guid), 
            headers={ 'User-Agent': random.choice(USER_AGENTS) }
        ).text

        return response