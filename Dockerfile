# Dockerfile
# Author: Rushy Panchal
# Date: March 8th, 2017
# Description: Docker services configuration.

FROM python:2.7.9
ENV PYTHONUNBUFFERED 1

# Install local code to server
RUN if [ ! -e /server ]; then mkdir /server; fi
WORKDIR /server
ADD requirements.txt /server/
RUN pip install -r requirements.txt
ADD . /server/
RUN python manage.py migrate
