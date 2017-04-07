#!/bin/bash
# docker/services/web.sh
# Author: Rushy Panchal
# Date: March 25th, 2017
# Description: Run TranscriptAPI web service.

cd "$APP_DIR"
docker/wait-for-it.sh -t 0 --strict db:5432 -- python manage.py runserver "0.0.0.0:$PORT"
