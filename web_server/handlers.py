import os
import mimetypes
from email.utils import formatdate
import logging

from web_server import http


class build_file_handler(object):
    def __init__(self, root_path):
        if root_path.startswith('.'):
            root_path = os.path.abspath(root_path)
        self.root_path = root_path

    def __call__(self, request):
        root_path = self.root_path
        path = os.path.join(root_path, request.path.lstrip('/'))
        path = os.path.abspath(path)
        if not path.startswith(root_path):
            return http.Response(http.FORBIDDEN, body='Forbidden')
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        if request.method in {'GET', 'HEAD'}:
            try:
                f = open(path, 'rb')
            except FileNotFoundError:
                return http.Response(http.NOT_FOUND, body='Not found')
            content_type, encoding = mimetypes.guess_type(path)
            content_len = os.fstat(f.fileno()).st_size
            if request.method == 'HEAD':
                f.close()
                r = http.Response(http.OK, body=None)
            else:
                r = http.Response(http.OK, body=f)
            (r.headers.add('Content-Length', content_len)
                        .add('Content-Type', content_type))
        else:
            raise ValueError('Only GET/HEAD methods supported')
        return r


def method_not_allowed(request):
    return http.Response(http.NOT_ALLOWED, body='Method Not Allowed')
