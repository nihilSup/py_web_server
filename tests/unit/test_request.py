import unittest

from web_server import http


def cases(cases):
    def run_cases(f):
        def wrapper(*args):
            for case in cases:
                case = (case, ) if not isinstance(case, tuple) else case
                f(*args, *case)
        return wrapper
    return run_cases


class TestHeaders(unittest.TestCase):

    def test_several_records(self):
        h = http.Headers()
        h.add('k', 1)
        h.add('k', 2)
        self.assertEqual(h.get_all('k'), [1, 2])
        self.assertEqual(h.get('k'), 2)

    def test_missing(self):
        h = http.Headers()
        self.assertEqual(h.get('k'), None)
        self.assertEqual(h.get_all('k'), [])

    def test_from_lines_empty(self):
        with self.assertRaises(Exception):
            http.Headers.from_lines([])

    @cases([
        [b'a'],
        [b'a: asdad'],
        [b'a:b'],
    ])
    def test_from_lines_many(self, lines):
        times = http.Headers.MAX_HEADERS_NUM + 1
        with self.assertRaises(Exception):
            http.Headers.from_lines(lines*times)

    def test_from_lines_valid(self):
        lines = """a:b\r\nc:d\r\n\r\n""".split('\r\n')
        r = http.Headers.from_lines(lines)
        self.assertEqual([r.get(k) for k in 'ac'], ['b', 'd'])

    def test_str(self):
        h = http.Headers()
        h.add('a', 'b').add('c', 'd')
        self.assertEqual('a: b\r\nc: d\r\n', str(h))
