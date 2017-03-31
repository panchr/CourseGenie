import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursegenie.settings")
import django
import json
import yaml
django.setup()
from core.models import *

CURRENT_TERM = Course.TERM_SPRING

with open("courses.json") as f:
	raw_data = json.load(f)

for record in raw_data:
	name = record["title"]
	number = record["listings"][0]["number"]
	department = record["listings"][0]["dept"]
	try:
		course = Course.objects.get(name=name, number=number, department=department)
		if course.term != Course.TERM_INCONSISTENT and course.term != CURRENT_TERM:
			course.term = Course.TERM_BOTH
			course.save()
	except Course.DoesNotExist:
		course = Course(name=name, number=number, department=department, term=CURRENT_TERM)
		course.save()
		length = len(record["listings"])
		if length > 1:
			list_crosses = []
			for k in range (1, length):
				number = record["listings"][k]["number"]
				department = record["listings"][k]["dept"]
				crosslisting = CrossListing(course=course, number=number, department=department)
				list_crosses.append(crosslisting)
			CrossListing.objects.bulk_create(list_crosses)
