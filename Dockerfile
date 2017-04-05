# Dockerfile
# Author: Rushy Panchal
# Date: March 8th, 2017
# Description: Docker services configuration.

FROM debian:8.7

RUN apt-get update

### Python ###
ENV PYTHONUNBUFFERED 1
RUN apt-get install -y git make python-dev build-essential libssl-dev \
	zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
	libncurses5-dev

ENV PYENV_ROOT "/pyenv"
ENV PATH       $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN if [ ! -e "$PYENV_ROOT" ]; then mkdir "$PYENV_ROOT"; fi
WORKDIR "$PYENV_ROOT"
RUN git clone git://github.com/yyuu/pyenv.git "$PYENV_ROOT"

ARG PYTHON_VERSION
RUN pyenv install "$PYTHON_VERSION"
RUN pyenv global "$PYTHON_VERSION"
RUN pyenv rehash

### Node ###
ARG NODE_VERSION
ENV NVM_DIR "/nvm"
ENV NODE_VERSION "$NODE_VERSION"
COPY docker/install-node.sh install-node.sh
RUN /bin/bash install-node.sh

ENV NODE_PATH "$NVM_DIR/versions/node/$NODE_VERSION/lib/node_modules"
ENV PATH      "$NVM_DIR/versions/node/$NODE_VERSION/bin:$PATH"

### Project Deployment ###
ARG APP_DIR
RUN if [ ! -e "$APP_DIR" ]; then mkdir "$APP_DIR"; fi
WORKDIR "$APP_DIR"
COPY requirements.txt "$APP_DIR/requirements.txt"
RUN apt-get install -y libpq-dev libyaml-dev
RUN pip install -r requirements.txt

COPY package.json "$APP_DIR/package.json"
RUN npm install

COPY . "$APP_DIR/"

# Port to expose
ARG PORT
EXPOSE $PORT
