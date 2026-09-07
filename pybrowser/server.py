#!/usr/bin/env python3

import sys
import os
import argparse

def serve_forever(host, port, cgi_directories):
    if sys.version_info < (3, 0):
        import CGIHTTPServer
        import BaseHTTPServer

        class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
            cgi_directories = cgi_directories

        server = BaseHTTPServer.HTTPServer((host, port), Handler)
    else:
        from http.server import CGIHTTPRequestHandler, HTTPServer

        handler = CGIHTTPRequestHandler
        handler.cgi_directories = cgi_directories

        server = HTTPServer((host, port), handler)

    print('Server started ({}, {})'.format(host, port))
    server.serve_forever()


if __name__ == '__main__':
    # Retrieve the PORT set by Render, defaulting to 8440 for local testing
    default_port = int(os.environ.get('PORT', 8440))

    parser = argparse.ArgumentParser(description='Run CGI Server.')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Server host address (default: 0.0.0.0 for Render)')
    parser.add_argument('--port', type=int, default=default_port,
                        help='Server port (defaults to $PORT env var on Render)')
    args = parser.parse_args()

    CGI_DIRECTORIES = ['/cgi-bin']
    serve_forever(args.host, args.port, CGI_DIRECTORIES)