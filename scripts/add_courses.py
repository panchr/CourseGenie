# scripts/add_courses.py
# CourseGenie
# Author: Kathy Fan
# Date: March 30th, 2017
# Description: script to help add course data into database.

import os
if os.path.dirname(os.getcwd()) == 'scripts':
	os.chdir('..')
	sys.path.append(os.path.abspath('..'))
else:
	sys.path.append(os.path.abspath('.'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursegenie.settings")
import django
django.setup()

from core.models import *

try:
	CURRENT_TERM = {'fall': Course.TERM_FALL,
		'spring': Course.TERM_SPRING}[sys.argv[1].lower()]
except (IndexError, KeyError):
	print("Usage: python scripts/add_courses.py {fall,spring}")
	sys.exit(1)

def main():
	with open("data/courses.json") as f:
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

			# Should eventually migrate this to take a set difference of current
			# listings (in the database) and listings present for the course; then,
			# perform the necessary updates.
			length = len(record["listings"])
			if length > 1:
				list_crosses = []
				for k in range (1, length):
					number = record["listings"][k]["number"]
					department = record["listings"][k]["dept"]
					crosslisting = CrossListing(course=course, number=number, department=department)
					list_crosses.append(crosslisting)
				CrossListing.objects.bulk_create(list_crosses)

if __name__ == '__main__':
	main()
