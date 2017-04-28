#!/bin/bash
# docker/services/init-web.sh
# Author: Rushy Panchal
# Date: April 24th, 2017
# Description: Initialize CourseGenie web service.

python scripts/add_courses.py fall
python scripts/add_courses.py spring
python scripts/add_requirements.py
