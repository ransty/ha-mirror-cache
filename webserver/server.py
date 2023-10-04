#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import os

import redis

conn = redis.Redis(host='redis', port=6379, db=0)
pub = conn.pubsub()

stream_channel = os.getenv("STREAM_CHANNEL", "cache")

FORBIDDEN_RESPONSE = {"Forbidden": "403"}
INVALID_REQUEST_RESPONSE = {"Invalid JSON": "JSON does not contain a package name!"}

class QueuePublisher(BaseHTTPRequestHandler):
    def _set_response(self, http_code=200):
        self.send_response(http_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_response(403)
        self.wfile.write(json.dumps(FORBIDDEN_RESPONSE).encode('utf-8'))

    def do_POST(self):
        if not self.headers['Content-Type'] == 'application/json':
            self._set_response(403)
            self.wfile.write(json.dumps(FORBIDDEN_RESPONSE).encode('utf-8'))
            return
        if self.headers['Content-Length']:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode('utf-8'))
            for key in request:
                if key == "package":
                    break
                else:
                    self._set_response(403)
                    self.wfile.write(json.dumps(INVALID_REQUEST_RESPONSE).encode('utf-8'))
                    return

            version = 'latest'
            for key, data in request.items():
                if key == "package":
                    package = data
                elif key == "version":
                    version = data

            logging.info("User requested package %s %s", package, version)
            conn.publish(stream_channel, json.dumps(request).encode('utf-8'))

        response = {"Queued": "OK"}
        self._set_response()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=QueuePublisher, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting Queue Publisher...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping Queue Publisher...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
