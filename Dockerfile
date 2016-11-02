FROM ubuntu:14.04
MAINTAINER Colin Alston <colin@praekelt.com>
RUN apt-get update && apt-get -y --force-yes install libjpeg-dev zlib1g-dev libxslt1-dev libpq-dev nginx supervisor python-dev python-pip libffi-dev

RUN pip install --upgrade pip

ENV PROJECT_ROOT /deploy/
ENV DJANGO_SETTINGS_MODULE testapp.testapp.settings.docker

WORKDIR /deploy/

COPY molo /deploy/molo
ADD requirements.txt /deploy/
ADD requirements-dev.txt /deploy/
ADD setup.py /deploy/
ADD README.rst /deploy/
ADD VERSION /deploy/

RUN pip install -e .
RUN molo scaffold testapp --include molo.servicedirectory ^servicedirectory/
RUN pip install -e testapp
ADD docker/settings.py /deploy/testapp/testapp/settings/docker.py

RUN mkdir -p /etc/supervisor/conf.d/
RUN mkdir -p /var/log/supervisor
RUN rm /etc/nginx/sites-enabled/default

ADD docker/nginx.conf /etc/nginx/sites-enabled/molo.conf
ADD docker/supervisor.conf /etc/supervisor/conf.d/molo.conf
ADD docker/supervisord.conf /etc/supervisord.conf
ADD docker/docker-start.sh /deploy/

RUN chmod a+x /deploy/docker-start.sh

EXPOSE 80

ENTRYPOINT ["/deploy/docker-start.sh"]
