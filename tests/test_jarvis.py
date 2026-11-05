import datetime as dt
import io
import json
import unittest
from unittest.mock import patch

import jarvis


class CommandTests(unittest.TestCase):
    def test_date_and_time(self):
        now = dt.datetime(2026, 11, 5, 15, 44, tzinfo=dt.timezone.utc)
        self.assertEqual(jarvis.respond('date', now), 'Local date: 2026-11-05')
        self.assertEqual(jarvis.respond('time', now), 'Local time: 15:44 UTC')

    def test_unknown_and_hello(self):
        self.assertIn("don't know", jarvis.respond('delete everything'))
        self.assertIn('Hello', jarvis.respond('  HI '))

    def test_ai_requires_explicit_enable(self):
        with patch('builtins.input', side_effect=['ai test', 'quit']), patch('jarvis.ask_ai') as call, patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(jarvis.main([]), 0)
        call.assert_not_called()
        self.assertIn('AI is disabled', output.getvalue())

    def test_bad_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            jarvis.ask_ai('hi', 'http://example.com/v1/chat/completions', 'model', 'key')
        with self.assertRaises(ValueError):
            jarvis.ask_ai('hi', 'https://user:pass@example.com/', 'model', 'key')

    def test_api_request_and_response(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, n):
                return json.dumps({'choices': [{'message': {'content': 'Hello back'}}]}).encode()
        class Opener:
            def open(self, request, timeout):
                self.request = request
                self.timeout = timeout
                return Response()
        opener = Opener()
        with patch('jarvis.urllib.request.build_opener', return_value=opener):
            result = jarvis.ask_ai('Hello', 'https://example.com/v1/chat/completions', 'test-model', 'secret')
        self.assertEqual(result, 'Hello back')
        self.assertEqual(json.loads(opener.request.data)['messages'][0]['content'], 'Hello')
        self.assertEqual(opener.timeout, 20)


if __name__ == '__main__':
    unittest.main()
