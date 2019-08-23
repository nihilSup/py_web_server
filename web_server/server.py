"""Server implementation"""
import socket
import os
import mimetypes
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.dummy import Pool

from web_server.http import (Request, Response, NOT_FOUND, BAD_REQUEST,
                             INTERNAL_ERROR)
from web_server.handlers import build_file_handler, method_not_allowed

log = logging.getLogger(__name__)


class HTTPServer(object):
    """
    Implementation of basic http server
    """

    def __init__(self, host, port, backlog=5, sock_timeout=2, handlers=None,
                 executor=None, workers=None):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.sock_timeout = sock_timeout
        self.req_handlers = handlers or {}
        self.workers = workers
        if not executor:
            executor = Pool(workers)
        self.executor = executor

    def add_handler(self, path, meth, handler):
        self.req_handlers[(path, meth)] = handler

    def serve_forever(self):
        with socket.socket() as s_socket:
            s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s_socket.bind((self.host, self.port))
            s_socket.listen(self.backlog)
            log.info(f'Listening on {self.host}:{self.port}')
            log.info(f'Workers {self.workers}')

            with self.executor as executor:
                handle_client = self.handle_client
                s_timeout = self.sock_timeout
                while True:
                    try:
                        c_socket, c_addr = s_socket.accept()
                        c_socket.settimeout(s_timeout)
                        log.info(f'Received connection from {c_addr}')
                        executor.apply_async(handle_client, (c_socket, c_addr))
                    except KeyboardInterrupt:
                        break

    def handle_client(self, c_socket, c_addr):
        with c_socket:
            try:
                request = Request.from_socket(c_socket)
            except Exception as e:
                log.info('Failed to parse request')
                log.exception(e)
                Response(BAD_REQUEST, body='Bad Request').send(c_socket)
            else:
                log.info(f'Received request {request}')
                for (path, meth), handler in self.req_handlers.items():
                    if request.path.startswith(path) and request.method == meth:
                        try:
                            response = handler(request)
                        except Exception as e:
                            log.exception(e)
                            response = Response(INTERNAL_ERROR)
                        finally:
                            break
                else:
                    log.info(f'No handlers for {path}')
                    response = Response(NOT_FOUND, body='Not Found')
                log.info(f'Created response:\n{response}')
                response.send(c_socket)
