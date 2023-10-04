import logging
import subprocess

import redis

conn = redis.Redis(host='redis', port=6379, db=0)

logging.info("Connecting to Redis...")

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
            subprocess.call(['pypi-mirror', 'download', '-d', '/opt/cache/', '-b', package])
            # Re-index simple
            subprocess.call(['pypi-mirror', 'create', '-d', '/opt/cache/', '-m', 'simple'], cwd='/opt/')
            subprocess.call(['python3', '-m', 'http.server'], cwd='/opt/')
    last_id = e[0]
