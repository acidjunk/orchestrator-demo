###############################
### BASE LAYER FOR IMAGES BELOW
FROM python:3.10-slim as base

RUN apt update && apt install -y git postgresql-client gcc g++ && rm -rf /var/lib/apt/lists/*

ADD requirements /usr/src/app/requirements

RUN pip3 install --no-cache-dir -r /usr/src/app/requirements/base.txt

#####################################################################
### IMAGE FOR LOCAL DEVELOPMENT WITH SOURCE FOLDERS COPIED INTO IMAGE
FROM base as local-test

RUN pip3 install --no-cache-dir -r /usr/src/app/requirements/all.txt

COPY . /usr/src/app

EXPOSE 8080

WORKDIR /usr/src/app

ENV PYTHONPATH=/usr/src/app

########################
### IMAGE FOR PRODUCTION
FROM base

ARG CI_COMMIT_SHA
ARG CI_COMMIT_TAG

LABEL maintainer="Automation <automation@company.com>"

WORKDIR /usr/src/app

COPY --chown=www-data:www-data . /usr/src/app

RUN echo "GIT_COMMIT_HASH=\"${CI_COMMIT_TAG:-$CI_COMMIT_SHA}\"" > /usr/src/app/company/version.py

EXPOSE 8080
USER www-data:www-data
CMD /usr/src/app/bin/server --worker-tmp-dir /dev/shm
