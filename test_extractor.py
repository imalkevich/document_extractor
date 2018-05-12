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

        loader = DocumentRawLoader('doc_guids.txt')

        # act
        xml = loader._load_doc_by_guid('some_guid')

        # assert
        self.assertEqual(xml, 'some_xml')

    def test_extract_text_from_xml(self):
        # arrange
        xml = '''
            <Document>
                <n-docbody>
                    <opinion.block>
                        <opinion.block.body>
                            <opinion.lead>
                                <opinion.body>
                                    <section id="1">
                                        <head>
                                        This is head 1.
                                        </head>
                                        <section.body>
                                            <para>
                                                <bop/>
                                                <bos/>
                                                <paratext>
                                                    <starpage.anchor>1</starpage.anchor>
                                                    The first section test text one goes here.
                                                    <eos/>
                                                    <bos/>
                                                    The first section test text two goes here.
                                                </paratext>
                                            </para>
                                        </section.body>
                                    </section>
                                    <section id="2">
                                        <head>
                                        This is head 2.
                                        </head>
                                        <section.body>
                                            <para>
                                                <bop/>
                                                <bos/>
                                                <paratext>
                                                    <starpage.anchor>2</starpage.anchor>
                                                    The second test text goes here.
                                                </paratext>
                                            </para>
                                        </section.body>
                                    </section>
                                </opinion.body>
                            </opinion.lead>
                        </opinion.block.body>
                    </opinion.block>
                </n-docbody>
            </Document>
        '''

        # act
        texts = DocumentRawLoader('doc_guids.txt')._extract_text_from_xml(xml)

        # arrange
        self.assertEqual(texts, [
            'The first section test text one goes here. The first section test text two goes here.',
            'The second test text goes here.'
        ])

    @mock.patch('extractor.loader.open')
    def test_save_text(self, mock_open):
        # arrange
        lines = ['one', 'two']

        loader = DocumentRawLoader('doc_guids.txt')
        loader._get_file_name = mock.MagicMock(return_value='file.txt')

        # act
        loader._save_text('guid', lines)

        # assert
        mock_open.assert_called_with('file.txt', 'w', encoding='utf-8')
        handle = mock_open()
        handle.assert_has_calls([
            mock.call.__enter__().write('one\n'), 
            mock.call.__enter__().write('two\n')
        ])

    @mock.patch('extractor.loader.open')
    def test_get_doc_guids(self, mock_open):
        # arrange
        loader = DocumentRawLoader('doc_guids.txt')
        loader.doc_guids_file = 'file.txt'

        # act
        loader._get_doc_guids()

        # assert
        mock_open.assert_called_with('file.txt', 'r')

    def test_get_doc_guids_from_line(self):
        # arrange
        line = '"one", "two", "three"'
        loader = DocumentRawLoader('doc_guids.txt')

        # act
        guids = loader._get_doc_guids_from_line(line)

        # assert
        self.assertEqual(guids, [ 'one', 'two', 'three' ])


    ''' DEBUG 
    def test_load(self):
        # arrange
        loader = DocumentRawLoader('doc_guids.txt')
        loader._get_doc_guids = mock.MagicMock(return_value=['I0f07d129334911d98b61a35269fc5f88'])

        # act
        loader.load()

        # assert
    '''

if __name__ == '__main__':
    unittest.main()
