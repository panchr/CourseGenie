#!/bin/bash
# install-docker.sh
# Author: Rushy Panchal
# Date: March 18th, 2017
# Description: Installs docker and docker-compose on the (Ubuntu 16.04) host.
# 	Adapted from: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04

apt-get update
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'
apt-get update
apt-cache policy docker-engine
apt-get install -y docker-engine

# Install the latest version of docker-compose (which is unavailable in the
# apt repositories).
apt-get install -y python-pip
pip install docker-compose

# Allow Docker to be used without sudo for the current user.
usermod -aG docker $(whoami)
