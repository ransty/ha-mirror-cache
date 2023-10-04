FROM python:3.8-slim-buster

COPY server.py /opt/

RUN pip install -U pip && pip install redis

ENTRYPOINT ["/usr/local/bin/python3.8"]
CMD ["/opt/server.py", "80"]
