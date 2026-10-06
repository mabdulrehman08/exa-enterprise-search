import json
import os
import unittest
from unittest.mock import patch

import app


class ResearchTests(unittest.TestCase):
    def test_corpus_and_extracts(self):
        self.assertEqual(len(app.RECORDS), 16)
        self.assertEqual(len(app.BY_ID), 16)
        for question in ('What blocks the Atlas EU launch?', 'How can Acme fix SSO?', 'What caused the search outage?'):
            result = app.research(question, 'preview')
            self.assertTrue(result['findings'])
            for finding in result['findings']:
                self.assertIn(finding['quote'], app.BY_ID[finding['sourceId']]['text'])
        self.assertEqual(app.research('What is the lunar cheese forecast?', 'preview')['findings'], [])

    def test_validation(self):
        for question, mode in [('', 'preview'), ('x'*801, 'preview'), (None, 'preview'), ('Atlas', 'other')]:
            with self.assertRaises(ValueError):
                app.research(question, mode)

    def test_exa_contract_and_no_fallback(self):
        base = 'https://knowledge.example.org/corpus'
        record = app.BY_ID['doc-01']
        quote = 'Target launch is October 14.'
        response = {'results': [{'url': base + '/doc-01.html'}], 'requestId': 'test-request',
                    'output': {'content': json.dumps({'findings': [{'text': 'The target is October 14.', 'sourceId': record['id'], 'quote': quote}]})}}
        with patch.dict(os.environ, {'CORPUS_BASE_URL': base, 'EXA_API_KEY': 'test-only'}), patch('app.exa_request', return_value=response) as request:
            result = app.research('When is Atlas launching?', 'exa')
            self.assertEqual(result['findings'][0]['quote'], quote)
            body = request.call_args.args[0]
            self.assertEqual(body['includeDomains'], ['knowledge.example.org/corpus'])
            self.assertEqual(body['type'], 'auto')
            self.assertTrue(body['contents']['highlights'])
            self.assertIn('outputSchema', body)
        with patch.dict(os.environ, {'CORPUS_BASE_URL': base}), patch('app.exa_request', side_effect=ValueError('API unavailable')):
            with self.assertRaisesRegex(ValueError, 'API unavailable'):
                app.research('When is Atlas launching?', 'exa')

    def test_reject_foreign_source_invented_and_stale_quotes(self):
        base = 'https://knowledge.example.org/corpus'
        data = {'results': [{'url': base + '/doc-01.html'}, {'url': 'https://attacker.example/doc-02.html'}],
                'output': {'content': {'findings': [
                    {'text': 'Invalid', 'quote': 'Target launch is September 30.', 'sourceId': 'doc-01'},
                    {'text': 'Foreign', 'quote': app.BY_ID['doc-02']['text'], 'sourceId': 'doc-02'},
                    {'text': 'Unknown', 'quote': 'Some unknown source content.', 'sourceId': 'bad'},
                    {'text': 'Too short', 'quote': 'Atlas', 'sourceId': 'doc-01'}]}}}
        findings, sources, _ = app.validate_response(data, base)
        self.assertEqual(findings, [])
        self.assertEqual([s['id'] for s in sources], ['doc-01'])

    def test_live_configuration(self):
        with patch.dict(os.environ, {'CORPUS_BASE_URL': '', 'EXA_API_KEY': ''}):
            with self.assertRaises(ValueError):
                app.research('Atlas launch?', 'exa')
        for url in ('http://localhost:8000', 'https://localhost/corpus', 'https://user:pass@example.org/corpus', 'https://example.org/?key=secret'):
            with patch.dict(os.environ, {'CORPUS_BASE_URL': url}):
                with self.assertRaises(ValueError):
                    app.base_url()

    def test_api_key_stays_in_header(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'{"results": []}'
        with patch.dict(os.environ, {'EXA_API_KEY': 'test-key'}), patch('app.urlopen', return_value=FakeResponse()) as call:
            app.exa_request({'query': 'Atlas'})
            request = call.call_args.args[0]
            self.assertEqual(request.full_url, 'https://api.exa.ai/search')
            self.assertEqual(request.get_header('X-api-key'), 'test-key')
            self.assertNotIn(b'test-key', request.data)


if __name__ == '__main__':
    unittest.main()
