#!/usr/bin/env python3
import json
import logging
import os
import subprocess

import redis

stream_channel = os.getenv("STREAM_CHANNEL", "cache")
conn = redis.Redis(host='redis', port=6379, db=0)
pub = conn.pubsub(ignore_subscribe_messages=True)
pub.subscribe(stream_channel) 

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

logging.info("Waiting for messages on %s stream", stream_channel)

while True:
    request = pub.get_message()
    if request:
        message = json.loads(request['data'].decode('utf-8'))
        # Version might not be set!
        version = None
        for key, data in message.items():
            if key == "package":
                package = data
            elif key == "version":
                version = data
        if package:
            if version:
                package = f'{package}=={version}'
            logging.info("Downloading package %s", package)
            subprocess.call(['pypi-mirror', 'download', '-d', '/opt/cache/', '-b', package])
            logging.info("Re-indexing simple")
            subprocess.call(['pypi-mirror', 'create', '-d', '/opt/cache/', '-m', 'simple'], cwd='/opt/')
