#!/bin/bash
# docker/digitalocean.sh
# CourseGenie
# Author: Rushy Panchal
# Date: March 25th, 2017
# Description: Initialize DigitalOcean droplet.

# Add 1G of swap space.
if [ ! -f /swapfile ]; then
	fallocate -l 1G /swapfile && chmod 400 /swapfile && mkswap /swapfile
	swapon /swapfile && echo '/swapfile none swap defaults 0 0' >> /etc/fstab
fi
