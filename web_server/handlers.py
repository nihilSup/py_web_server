import os
import mimetypes

from web_server.http import Response


def build_file_handler(root_path):
    def file_handler(request):
        path = os.path.join(root_path, request.path.lstrip('/'))
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        print(f'Path to open: {path}')
        try:
            f = open(path, 'rb')
            r = Response('200 OK', body=f)
            content_type, encoding = mimetypes.guess_type(path)
            r.headers.add("content-type", content_type)
            return r
        except FileNotFoundError:
            return Response('404 Not found', body='Not found')
    return file_handler


def method_not_allowed(request):
    return Response('405 Method Not Allowed', body='Method Not Allowed')
