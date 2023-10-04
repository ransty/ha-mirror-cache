#!/usr/bin/env python3
import logging
import subprocess

import redis

conn = redis.Redis(host='redis', port=6379, db=0)

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
logging.info("Connecting to Redis...")

server_on = False

while True:
    last_id = '$'
    events = conn.xread({"cache": last_id}, block=0, count=10)
    for _, e in events:
        request = e[0][1]
        for key, data in request.items():
            if key.decode('utf-8') == "package":
                package = data.decode('utf-8')
            elif key.decode('utf-8') == "version":
                version = data.decode('utf-8')
        if package:
            if version:
                package = f'{package}=={version}'
            logging.info("Downloading package %s", package)
            subprocess.call(['pypi-mirror', 'download', '-d', '/opt/cache/', '-b', package])
            logging.info("Re-indexing simple")
            subprocess.call(['pypi-mirror', 'create', '-d', '/opt/cache/', '-m', 'simple'], cwd='/opt/')
            if not server_on:
                logging.info("Spawning http.server")
                subprocess.Popen(['python3', '-m', 'http.server'], cwd='/opt/')
                server_on = True
    last_id = e[0]
