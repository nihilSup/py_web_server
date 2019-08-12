"""HTTP parsing helpers"""
import typing
import itertools as it
import io
import reprlib
from collections import defaultdict, namedtuple
from email.utils import formatdate


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
        return self

    def add_if_none(self, key, val):
        if key not in self:
            self.add(key, val)
        return self

    @classmethod
    def from_lines(cls, lines):
        headers = cls()
        for line in it.islice(lines, cls.MAX_HEADERS_NUM):
            if line in (b'\r\n', b'\n', b''):
                break
            line = line.decode('ASCII')
            try:
                name, _, value = line.partition(':')
            except ValueError:
                raise ValueError(f'Malformed header: {line}')
            value = value.strip()
            headers.add(name, value)
        else:
            raise Exception('Malformed headers: no headers,' +
                            ' too many, no blank line')
        return headers

    def __iter__(self):
        for name, values in self._headers_dct.items():
            for value in values:
                yield name, value

    def __contains__(self, key):
        return key in self._headers_dct

    def __str__(self):
        return "".join(f"{name}: {value}\r\n" for name, value in self)

    def __bytes__(self):
        return str(self).encode()


class Request(typing.NamedTuple):
    method:  str
    path:    str
    vers:    str
    headers: Headers

    LINE_MAX_SIZE = 10*1024

    @classmethod
    def _read_line(cls, rb_file):
        line = rb_file.readline(cls.LINE_MAX_SIZE)
        if len(line) >= cls.LINE_MAX_SIZE:
            raise ValueError('Too long request line')
        return line

    @classmethod
    def from_socket(cls, socket):
        with socket.makefile('rb') as rb_file:
            line = cls._read_line(rb_file)
            meth, path, vers = cls._parse_request_line(line)
            headers = Headers.from_lines(cls._read_line(rb_file)
                                         for _ in it.count())
            return cls(meth, path, vers, headers)

    @classmethod
    def _parse_request_line(cls, line):
        if not line:
            raise ValueError('Empty request line')
        req_line = line.decode('ASCII').rstrip('\r\n')
        try:
            meth, path_query, vers = req_line.split(' ')
            path, query = path_query.split('?')
        except ValueError:
            raise ValueError(f'Malformed request line: {req_line}')
        return meth, path, vers


# Probably refactor with dataclasses
class Response(object):

    def __init__(self, status, headers=None, body=None, server='otuserver'):
        self.status = status
        self.headers = headers or Headers()
        (self.headers.add_if_none('Date', formatdate(timeval=None,
                                                     localtime=False,
                                                     usegmt=True))
                     .add_if_none('Server', server)
                     .add_if_none('Connection', 'close'))
        if body and not isinstance(body, io.IOBase):
            body = io.BytesIO(body.encode())
        self.body = body

    def send(self, socket):
        msg = (
            f'HTTP/1.1 {self.status}\r\n' +
            str(self.headers) +
            '\r\n'
        )
        socket.sendall(msg.encode())
        if self.body:
            socket.sendfile(self.body)
            self.body.close()

    def __repr__(self):
        return (f'{self.__class__.__name__}' +
                f'(status={self.status}, headers={self.headers}, ' +
                f'body={reprlib.repr(self.body)})')

OK = '200 OK'
NOT_FOUND = '404 Not Found'
NOT_ALLOWED = '405 Method Not Allowed'
INTERNAL_ERROR = '503 Internal Server Error'
BAD_REQUEST = '400 Bad Request'
