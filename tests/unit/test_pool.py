import unittest

from web_server.executors import ThreadPool


class TestPool(unittest.TestCase):
    def test_pool(self):
        with ThreadPool(10) as p:
            for i in range(10):
                p.submit(lambda i: print(i), i)
