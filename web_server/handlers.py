import os
import mimetypes
from email.utils import formatdate

from web_server import http


def build_file_handler(root_path, server='otuserver'):
    if root_path.startswith('.'):
        root_path = os.path.abspath(root_path)

    def file_handler(request):
        path = os.path.join(root_path, request.path.lstrip('/'))
        path = os.path.abspath(path)
        if not path.startswith(root_path):
            return http.Response(http.FORBIDDEN, body='Forbidden')
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        try:
            if request.method in {'GET', 'HEAD'}:
                f = open(path, 'rb')
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
        except FileNotFoundError:
            return http.Response(http.NOT_FOUND, body='Not found')

    return file_handler


def method_not_allowed(request):
    return http.Response(http.NOT_ALLOWED, body='Method Not Allowed')
