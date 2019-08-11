import os
import mimetypes
from email.utils import formatdate

from web_server.http import Response


def build_file_handler(root_path, server='otuserver'):
    def file_handler(request):
        path = os.path.join(root_path, request.path.lstrip('/'))
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        try:
            f = open(path, 'rb')
            if request.method == 'GET':
                r = Response('200 OK', body=f)
                content_type, encoding = mimetypes.guess_type(path)
                (r.headers.add('Date', formatdate(timeval=None,
                                                  localtime=False,
                                                  usegmt=True))
                          .add('Server', server)
                          .add('Content-Length', os.fstat(f.fileno()).st_size)
                          .add('Content-Type', content_type)
                          .add('Connection', 'close'))
            elif request.method == 'HEAD':
                f.close()
                r = Response('200 OK', body=None)
            else:
                raise ValueError('Only GET/HEAD methods supported')
            return r
        except FileNotFoundError:
            return Response('404 Not found', body='Not found')
    return file_handler


def method_not_allowed(request):
    return Response('405 Method Not Allowed', body='Method Not Allowed')
