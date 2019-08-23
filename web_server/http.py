"""HTTP parsing helpers"""
import typing
import itertools as it
import io
import reprlib
import urllib.parse
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
            if line == '\r\n':
                break
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
    RECV_SIZE = 4096

    @classmethod
    def _read_line(cls, rb_file):
        line = rb_file.readline(cls.LINE_MAX_SIZE)
        if len(line) >= cls.LINE_MAX_SIZE:
            raise ValueError('Too long request line')
        return line.decode('ASCII')

    @classmethod
    def lines_from_socket_file(cls, socket):
        """Utility generator in file like handling"""
        with socket.makefile('rb') as rb_file:
            while True:
                yield cls._read_line(rb_file)

    @classmethod
    def lines_from_socket(cls, socket):
        buff = b''
        size = min(cls.LINE_MAX_SIZE, cls.RECV_SIZE)
        while True:
            if len(buff) > cls.LINE_MAX_SIZE:
                raise ValueError('Line is too long')
            elif b'\r\n' in buff:
                line, buff = buff.split(b'\r\n', 1)
                yield line.decode('ASCII') + '\r\n'
            else:
                data = socket.recv(min(cls.LINE_MAX_SIZE - len(buff),
                                       size))
                if not data:
                    break
                buff += data
        if buff:
            return buff

    @classmethod
    def from_socket(cls, socket):
        lines = cls.lines_from_socket(socket)
        try:
            line = next(lines)
        except StopIteration:
            raise ValueError('Empty request line')
        meth, path, vers = cls._parse_request_line(line)
        headers = Headers.from_lines(lines)
        lines.close()
        return cls(meth, path, vers, headers)

    @staticmethod
    def _parse_request_line(line):
        if not line:
            raise ValueError('Empty request line')
        req_line = line.rstrip('\r\n')
        try:
            meth, path_query, vers = req_line.split(' ')
            parsed = urllib.parse.urlparse(path_query)
            path = urllib.parse.unquote(parsed.path)
        except ValueError:
            raise ValueError(f'Malformed request line: "{req_line}"')
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

    def __str__(self):
        return '\n'.join([
             f'{self.status}',
             f'{self.headers}',
             f'{reprlib.repr(self.body)})'
        ])

OK = '200 OK'
BAD_REQUEST = '400 Bad Request'
FORBIDDEN = '403 Forbidden'
NOT_FOUND = '404 Not Found'
NOT_ALLOWED = '405 Method Not Allowed'
INTERNAL_ERROR = '500 Internal Server Error'
