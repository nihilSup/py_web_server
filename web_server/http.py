"""HTTP parsing helpers"""
import typing
from collections import defaultdict, namedtuple
import itertools as it
import io


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

    @classmethod
    def from_lines(cls, lines):
        headers = cls()
        for line in it.islice(lines, cls.MAX_HEADERS_NUM):
            print('bla', line)
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
            meth, path, vers = req_line.split(' ')
        except ValueError:
            raise ValueError(f'Malformed request line: {req_line}')
        return meth, path, vers


class Response(object):

    def __init__(self, status, headers=None, body=None):
        self.status = status
        self.headers = headers or Headers()
        if body:
            if not isinstance(body, io.IOBase):
                self.body = io.BytesIO(body.encode())
            else:
                self.body = body
        else:
            self.body = None

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
