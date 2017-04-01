# scripts/add_profile.py
# Author: Kathy Fan
# Date: April 1st, 2017
# adds information from transcript into database

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursegenie.settings")
import django
import json
import yaml
django.setup()
from core.models import *

with open("sample_transcript_kathy.json") as f:
	raw_data = json.load(f)

user.username = raw_data["netid"]
t = raw_data["transcript"]
list_records = []
for semester in t["courses"]:
	courses = t["courses"][semester]
	for course in courses:
		grade = t["grades"][course]
		list_records.append(Record(course=course, grade=grade, semester=semester, parent=profile))

Record.objects.bulk_create(list_records)