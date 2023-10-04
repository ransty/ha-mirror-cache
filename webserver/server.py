#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import os

import redis


stream_key = os.getenv("STREAM_KEY", "cache")

FORBIDDEN_RESPONSE = {"Forbidden": "403"}
INVALID_REQUEST_RESPONSE = {"Invalid JSON": "JSON does not conform to {'package': 'version'}"}

class S(BaseHTTPRequestHandler):
    def _set_response(self, http_code=200):
        self.send_response(http_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response(403)
        self.wfile.write(json.dumps(FORBIDDEN_RESPONSE).encode('utf-8'))

    def do_POST(self):
        if not self.headers['Content-Type'] == 'application/json':
            self._set_response(403)
            self.wfile.write(json.dumps(FORBIDDEN_RESPONSE).encode('utf-8'))
            return
        if self.headers['Content-Length']:
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            request = json.loads(post_data.decode('utf-8'))
            for key in request:
                if key == "package":
                    break
                else:
                    self._set_response(403)
                    self.wfile.write(json.dumps(INVALID_REQUEST_RESPONSE).encode('utf-8'))
                    return

            for key, data in request.items():
                if key == "package":
                    package = data
                elif key == "version":
                    version = data

            logging.info("User requested package %s %s", package, version)
            self.queue_request(request)

        response = {"Queued": "OK"}
        self._set_response()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def queue_request(self, request):
        """
        Adds a new package to be mirrored to the queue
        If version is not provided, latest will be grabbed
        :param request: The JSON request to pass to the broker
        """
        conn = redis.Redis(host='redis', port=6379, db=0)
        conn.xadd(stream_key, request)
        return

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
