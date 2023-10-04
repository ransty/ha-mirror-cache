FROM python:3.8-slim-buster

COPY consumer.py /opt/

RUN pip install -U pip && pip install redis python-pypi-mirror \
    && mkdir /opt/cache

ENTRYPOINT ["/usr/local/bin/python3.8"]
CMD ["-u", "/opt/consumer.py"]
