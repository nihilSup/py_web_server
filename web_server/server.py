"""Server implementation"""
import socket
import os
import mimetypes

from web_server.http import Request, Response
from web_server.handlers import build_file_handler


class HTTPServer(object):
    """
    Implementation of basic http server
    """

    def __init__(self, host, port, backlog=5):
        self.host = host
        self.port = port
        self.req_handlers = {}
        self.backlog = backlog
        print(f'Initialized server on {self.host}:{self.port}')

    def add_handler(self, path, handler):
        self.req_handlers[path] = handler

    def serve_forever(self):
        with socket.socket() as s_socket:
            s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s_socket.bind((self.host, self.port))
            s_socket.listen(self.backlog)
            print('Listening on {}:{}'.format(self.host, self.port))

            while True:
                c_socket, c_addr = s_socket.accept()
                print('Received connection from', c_addr)
                self.handle_client(c_socket, c_addr)

    def handle_client(self, c_socket, c_addr):
        with c_socket:
            try:
                request = Request.from_socket(c_socket)
            except Exception:
                print('Failed to parse request')
                Response('400 Bad Request', body='Bad Request').send(c_socket)
            else:
                print('Received request', request)
                for path, handler in self.req_handlers.items():
                    if request.path.startswith(path):
                        try:
                            response = handler(request)
                        except Exception as e:
                            print(f'Error while processing {e}')
                            response = Response('503 Internal Server Error')
                        finally:
                            break
                else:
                    print(f'No handlers for {path}')
                    response = Response('404 Not found', body='Not Found')
                response.send(c_socket)


if __name__ == '__main__':
    server = HTTPServer('localhost', 9997)
    document_root = os.path.abspath('./')
    server.add_handler('/', build_file_handler(document_root))
    server.serve_forever()
