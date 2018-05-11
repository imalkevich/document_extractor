'''
Tests for extractor module.
'''

import unittest
import unittest.mock as mock

from extractor.loader import DocumentRawLoader

class DocumentRawLoaderTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('extractor.loader.requests')
    def test_load_doc_by_guid(self, mock_requests):
        # arrange
        mock_response = mock.Mock()
        mock_response.text = 'some_xml'
        mock_session = mock.MagicMock()
        mock_session.get = mock.MagicMock(return_value=mock_response)
        mock_requests.session = mock.MagicMock(return_value=mock_session)

        loader = DocumentRawLoader([])

        # act
        xml = loader._load_doc_by_guid('some_guid')

        # assert
        self.assertEqual(xml, 'some_xml')


if __name__ == '__main__':
    unittest.main()
