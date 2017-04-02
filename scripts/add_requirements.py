# scripts/add_requirements.py
# CourseGenie
# Author: Kathy Fan
# Date: March 31st, 2017
# Description: script to help add major and requirements data into database.

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursegenie.settings")
import django
import json
import yaml
django.setup()
from core.models import *

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
							try: # in case course isn't in database
								course = Course.objects.get(department=dept, number=num) 
								req.courses.add(course)
							except Course.DoesNotExist: # either actually not in database, or is a cross listing
								try:
									crossed = CrossListing.objects.get(department=dept, number=num)
									req.courses.add(crossed.course)
								except CrossListing.DoesNotExist:
									# do something to tell us c was not added
									pass
			
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
						try: # in case course isn't in database
							course = Course.objects.get(department=dept, number=num) 
							req.courses.add(course)
						except Course.DoesNotExist: # either actually not in database, or is a cross listing
							try:
								crossed = CrossListing.objects.get(department=dept, number=num)
								req.courses.add(crossed.course)
							except CrossListing.DoesNotExist:
								# do something to tell us c was not added	
								pass			

	if record == "certificates":
		for cert in raw_data[record]:
			name = cert["name"]
			try:
				certificate = Certificate.objects.get(name=name)
			except Certificate.DoesNotExist:
				short_name = cert["short_name"]
				certificate = Certificate(name=name, short_name=short_name)
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
						try: # in case course isn't in database
							course = Course.objects.get(department=dept, number=num) 
							req.courses.add(course)
						except Course.DoesNotExist: # either actually not in database, or is a cross listing
							try:
								crossed = CrossListing.objects.get(department=dept, number=num)
								req.courses.add(crossed.course)
							except CrossListing.DoesNotExist:
								# do something to tell us c was not added	
								pass

	if record == "degrees":
		for deg in raw_data[record]:
			name = deg["name"]
			try:
				degree = Degree.objects.get(name=name)
			except Certificate.DoesNotExist:
				short_name = deg["short_name"]
				degree = Degree(name=name, short_name=short_name)
				degree.save()
				
				# add requirements that belong to the degree
				for key in deg["requirements"]:
					name = key["name"]
					t = key["type"]
					number = key["number"]
					notes = key["notes"] # not all data has this
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=degree)
					req.save()
					# add courses via loop, req.courses.add(course)
					for c in key["courses"]:
						dept = c[:3]
						num = c[4:]
						try: # in case course isn't in database
							course = Course.objects.get(department=dept, number=num) 
							req.courses.add(course)
						except Course.DoesNotExist: # either actually not in database, or is a cross listing
							try:
								crossed = CrossListing.objects.get(department=dept, number=num)
								req.courses.add(crossed.course)
							except CrossListing.DoesNotExist:
								# do something to tell us c was not added	
								pass				