#!/bin/bash
# docker/services/web.sh
# Author: Rushy Panchal
# Date: March 25th, 2017
# Description: Run CourseGenie web service.

cd "$APP_DIR"
if [ "$ENV" = "production" ]; then
	UWSGI_PORT="$PORT" docker/wait-for-it.sh -t 0 --strict db:5432 -- uwsgi --ini wsgi.ini
else
	docker/wait-for-it.sh -t 0 --strict db:5432 -- python manage.py runserver "0.0.0.0:$PORT"
fi
