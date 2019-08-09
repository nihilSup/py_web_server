import unittest

from web_server import request


class TestHeaders(unittest.TestCase):

    def test_several_records(self):
        h = request.Headers()
        h.add('k', 1)
        h.add('k', 2)
        self.assertEqual(h.get_all('k'), [1, 2])
        self.assertEqual(h.get('k'), 2)

    def test_missing(self):
        h = request.Headers()
        self.assertEqual(h.get('k'), None)
        self.assertEqual(h.get_all('k'), [])