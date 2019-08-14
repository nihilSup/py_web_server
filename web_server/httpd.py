"""Main entry point"""
import argparse
import logging
from multiprocessing import Pool

from web_server.server import HTTPServer
from web_server.handlers import build_file_handler, method_not_allowed


def main():
    args = parse_args()
    logging.basicConfig(filename=args.log, level=args.loglevel,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(args.host, args.port, workers=args.workers)
    server.add_handler('/', 'GET', build_file_handler(args.root))
    server.add_handler('/', 'HEAD', build_file_handler(args.root))
    server.add_handler('/', 'POST', method_not_allowed)
    server.add_handler('/', 'PUT', method_not_allowed)
    server.serve_forever()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--host", type=str, default='localhost',
                        help='hostname to listen')
    parser.add_argument("-p", "--port", type=int, default=8080,
                        help='tcp port to listen')
    parser.add_argument('-r', '--root', type=str,
                        default='./tests/integration',
                        help='path to DOCUMENT_ROOT')
    parser.add_argument('-w', '--workers', type=int, default=10,
                        help='number of workers')
    parser.add_argument("-l", "--log", action="store", default=None,
                        help='path to log file')
    parser.add_argument('-v', '--verbose', action='store_const',
                        dest='loglevel', const=logging.INFO,
                        help='set logging level INFO', default=logging.ERROR)
    parser.add_argument('-d', '--debug', action='store_const',
                        dest='loglevel', const=logging.DEBUG,
                        help='set logging level DEBUG')
    return parser.parse_args()


if __name__ == '__main__':
    main()
