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
	if record == "majors": # list of all majors; each major is a dictionary
		for maj in raw_data[record]:
			name = maj["name"]
			try:
				major = Major.objects.get(name=name)
			except Major.DoesNotExist:
				short_name = maj["short_name"]
				degree = maj["degree"]
				major = Major(name=name, short_name=short_name, degree=degree)
				major.save()
				
				# add tracks
				for key in maj["tracks"]:
					name = key
					track = Track(major=major, name=name)
					track.save()
					for k in maj["tracks"][key]:
						name = k["name"] # not sure if we need this; currently mostly missing
						t = k["type"]
						number = k["number"]
						notes = k["notes"] # not all data has this
						req = Requirement(name=name, t=t, number=number, notes=notes, parent=track)
						req.save()
						# add courses via loop, req.courses.add(course)
						for c in k["courses"]:
							dept = c[:3]
							num = c[4:]
							course = Course.objects.get(department=dept, number=num) 
							req.courses.add(course) # best way to deal with: if course isn't in Course database?
			
				# add requirements that belong to the major
				for key in maj["requirements"]:
					name = key["name"]
					t = key["type"]
					number = key["number"]
					notes = key["notes"] # not all data has this
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=major)
					req.save()
					# add courses via loop, req.courses.add(course)
					for c in key["courses"]:
						dept = c[:3]
						num = c[4:]
						course = Course.objects.get(department=dept, number=num) 
						req.courses.add(course) # best way to deal with: if course isn't in Course database?					

	if record == "certificates":
		for cert in raw_data[record]:
			name = cert["name"]
			try:
				certificate = Certificate.objects.get(name=name)
			except Certificate.DoesNotExist:
				short_name = cert["short_name"]
				certificate = Certificate(name=name, short_name=short_name) # is it necessary to have a short_name for certificate? might be useful for display?
				certificate.save()
				
				# add requirements that belong to the certificate
				for key in cert["requirements"]:
					name = key["name"]
					t = key["type"]
					number = key["number"]
					notes = key["notes"] # not all data has this
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=certificate)
					req.save()
					# add courses via loop, req.courses.add(course)
					for c in key["courses"]:
						dept = c[:3]
						num = c[4:]
						course = Course.objects.get(department=dept, number=num) 
						req.courses.add(course) # best way to deal with: if course isn't in Course database?

