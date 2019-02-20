FROM ubuntu:16.04
LABEL maintainer Bodastage Engineering <engineering@bodastage.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y netcat git wget zlib1g-dev libffi-dev \
    libssl-dev build-essential

RUN mkdir -p /deploy && mkdir -p /reports && mkdir -p /app
COPY ./generate_report_worker.py /app/generate_report_worker.py

COPY ./requirements.txt /deploy/requirements.txt

 WORKDIR /app

# Install python 3.7
RUN mkdir /tmp/Python37 \
    && cd /tmp/Python37 \
    && wget https://www.python.org/ftp/python/3.7.1/Python-3.7.1.tgz \
    && tar xzf /tmp/Python37/Python-3.7.1.tgz \
    && cd /tmp/Python37/Python-3.7.1 \
    && ./configure \
    && make altinstall \
    && pip3.7 install -r /deploy/requirements.txt


CMD ["/usr/local/bin/python3.7", "/app/generate_report_worker.py"]