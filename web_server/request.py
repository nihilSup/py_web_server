"""HTTP request parsing helpers"""
import typing
from collections import defaultdict
import itertools as it


class Headers(object):

    MAX_HEADERS_NUM = 100

    def __init__(self):
        self._headers_dct = defaultdict(list)

    def get(self, key):
        try:
            return self.get_all(key)[-1]
        except IndexError:
            return None

    def get_all(self, key):
        return self._headers_dct[key]

    def add(self, key, val):
        self._headers_dct[key].append(val)

    @classmethod
    def from_lines(cls, lines):
        headers = cls()
        for line in it.islice(lines, cls.MAX_HEADERS_NUM):
            if line in (b'\n\r', b'\n', ''):
                break
            line = line.decode('ASCII')
            try:    
                name, _, value = line.partition(':')
            except ValueError:
                raise ValueError(f'Malformed header: {line}')
            value = value.strip()
            headers.add(name, value)
        else:
            raise Exception('To many headers')
        return headers


class Request(typing.NamedTuple):
    method:  str
    path:    str
    vers:    str
    headers: Headers

    MAX_HEADERS_NUM = 100

    @classmethod
    def from_lines(cls, lines):
        meth, path, vers = cls._parse_request_line(lines)
        headers = Headers.from_lines(lines)
        return cls(meth, path, vers, headers)

    @classmethod
    def _parse_request_line(cls, lines):
        try:
            line = next(lines)
            if not line:
                raise ValueError('Empty request line')
            req_line = line.decode('ASCII').rstrip('\r\n')
        except StopIteration:
            raise ValueError('Empty request')
        try:
            meth, path, vers = req_line.split(' ')
        except ValueError:
            raise ValueError(f'Malformed request line: {req_line}')
        return meth, path, vers
