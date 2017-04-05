# scripts/add_profile.py
# Author: Kathy Fan
# Date: April 1st, 2017
# adds information from transcript into database

# assuming data format is as displayed in output; see sample transcript data
# does transcript parser grab everything? name? year?
# assumes profile already exist; just adds in records from transcript
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursegenie.settings")
import django
import json
import yaml
django.setup()
from core.models import *

with open("sample_transcript_kathy.json") as f:
	raw_data = json.load(f)

u = raw_data["user"]
id = u["netid"]
first = u["first_name"]
last = u["last_name"]
profile = Profile.objects.get(user__username=id)
profile.user.first_name = first
profile.user.last_name = last
t = raw_data["transcript"]
list_records = []
for semester in t["courses"]:
	courses = t["courses"][semester]
	for course in courses:
		grade = t["grades"][course]
		list_records.append(Record(course=course, grade=grade, semester=semester, profile=profile))

Record.objects.bulk_create(list_records)