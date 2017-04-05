# scripts/add_courses_combined.py
# CourseGenie
# Author: Kathy Fan
# Date: April 3rd, 2017
# adds in course data in usg data and class data; v3 of original add_courses.py

import sys
import os
if os.path.dirname(os.getcwd()) == 'scripts':
	os.chdir('..')
	sys.path.append(os.path.abspath('..'))
else:
	sys.path.append(os.path.abspath('.'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursegenie.settings")
import django
django.setup()
import json

from core.models import *

try:
	CURRENT_TERM = {'fall': Course.TERM_FALL,
		'spring': Course.TERM_SPRING}[sys.argv[1].lower()]
except (IndexError, KeyError):
	print("Usage: python scripts/add_courses.py {fall,spring}")
	sys.exit(1)

def main():
	with open("data/usg-courses.json") as f:
		raw_data = json.load(f)

	for record in raw_data:
		name = record["title"]
		id_number = record["course_id"]
		number = int(record["catalog_number"][:3])
		try: 
			dept = Department.objects.get(short_name=record["subj_code"])
		except Department.DoesNotExist:
			dept = Department(short_name=record["subj_code"], name=record["subj_name"])
			dept.save()
		if len(record["catalog_number"]) > 3:
			letter = record["catalog_number"][3:4]
		else:
			letter = ""
		department = record["subj_code"]
		try:
			course = Course.objects.get(name=name, course_id=id_number, number=number, department=department, letter=letter)
			if course.term != Course.TERM_INCONSISTENT and course.term != CURRENT_TERM:
				course.term = Course.TERM_BOTH
				course.save()
		except Course.DoesNotExist:
			course = Course(name=name, number=number, course_id=id_number, department=department, letter=letter, term=CURRENT_TERM)
			course.save()

			# Should eventually migrate this to take a set difference of current
			# listings (in the database) and listings present for the course; then,
			# perform the necessary updates.
			if "crosslistings" in record:
				list_crosses = []
				for item in record["crosslistings"]:
					number = int(item["catalog_number"][:3])
					if len(item["catalog_number"]) > 3:
						letter = item["catalog_number"][3:4]
					else:
						letter = ""
					department = item["subject"]
					crosslisting = CrossListing(course=course, number=number, letter=letter, department=department)
					list_crosses.append(crosslisting)
				CrossListing.objects.bulk_create(list_crosses)

	f.close()

	with open("data/courses.json") as f:
		raw_data = json.load(f)

		for record in raw_data:
			try: 
				course = Course.objects.get(course_id=record["courseid"])
				course.area = record["area"]
				try:
					area = Area.objects.get(short_name=record["area"])
				except Area.DoesNotExist:
					area = Area(short_name=record["area"])
					area.save()
				course.save()
			except Course.DoesNotExist:
				pass
	f.close()
if __name__ == '__main__':
	main()