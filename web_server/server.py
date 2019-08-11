"""Server implementation"""
import socket

from web_server.http import Request


class HTTPServer(object):
    """
    Implementation of basic http server
    """

    LINE_MAX_SIZE = 10*1024

    def __init__(self, host, port, document_root, backlog=5):
        self.host = host
        self.port = port
        self.document_root = document_root
        self.backlog = backlog

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
            request = Request.from_socket(c_socket)
            print('Received request', request)


if __name__ == '__main__':
    server = HTTPServer('localhost', 9997)
    server.serve_forever()
