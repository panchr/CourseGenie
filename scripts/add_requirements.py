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
						t = key["type"]
						name = key.get("name", t.replace('-', ' ').title())
						number = k["number"]
						notes = k["notes"] # not all data has this
						req = Requirement(name=name, t=t, number=number, notes=notes, parent=track)
						req.save()
						# add courses via loop, req.courses.add(course)
						for c in k["courses"]:
							# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
							m = re.match(r"^([A-Z]{3}) ?>= ?([0-9]{3})$", c)
							if m:
								dept = m.group(1)
								at_least = int(m.group(2))
								satisfied = Course.objects.filter(department=dept, number__gte=n)
								req.courses.add(satisfied)
							# DEPT* shortcut
							m = re.match(r"^([A-Z]{3})(\*)$", c)
							if m:
								dept = m.group(1)
								satisfied = Course.objects.filter(department=dept)
								req.courses.add(satisfied)							
							# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
							m = re.match(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$", c)
							if m:
								dept = m.group(1)
								area = m.group(2)
								at_least = int(m.group(3))
								satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
								req.courses.add(satisfied)
							# * shortcut
							m = re.match(r"^(\*)$", c)
							if m:
								satisfied = Course.objects.all()
								req.courses.add(satisfied)		
							# *>=NUMBER
							m = re.match(r"^\* ?>= ?([0-9]{3})$", c)
							if m:
								at_least = int(m.group(1))
								satisfied = Course.objects.filter(number__gte=n)
								req.courses.add(satisfied)						
							# special
							m = re.match(r"^special$", c)
							if m:
								pass					
							# theme:something
							m = re.match(r"^theme:", c)
							if m:
								pass			
							# @RUSHY will handle OR 				
							# regular course entry
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
					t = key["type"]
					name = key.get("name", t.replace('-', ' ').title())
					number = key["number"]
					notes = key["notes"] # not all data has this
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=major)
					req.save()
					# add courses via loop, req.courses.add(course)
					for c in key["courses"]:
							# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
							m = re.match(r"^([A-Z]{3}) ?>= ?([0-9]{3})$", c)
							if m:
								dept = m.group(1)
								at_least = int(m.group(2))
								satisfied = Course.objects.filter(department=dept, number__gte=n)
								req.courses.add(satisfied)
							# DEPT* shortcut
							m = re.match(r"^([A-Z]{3})(\*)$", c)
							if m:
								dept = m.group(1)
								satisfied = Course.objects.filter(department=dept)
								req.courses.add(satisfied)							
							# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
							m = re.match(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$", c)
							if m:
								dept = m.group(1)
								area = m.group(2)
								at_least = int(m.group(3))
								satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
								req.courses.add(satisfied)
							# * shortcut
							m = re.match(r"^(\*)$", c)
							if m:
								satisfied = Course.objects.all()
								req.courses.add(satisfied)		
							# *>=NUMBER
							m = re.match(r"^\* ?>= ?([0-9]{3})$", c)
							if m:
								at_least = int(m.group(1))
								satisfied = Course.objects.filter(number__gte=n)
								req.courses.add(satisfied)						
							# special
							m = re.match(r"^special$", c)
							if m:
								pass					
							# theme:something
							m = re.match(r"^theme:", c)
							if m:
								pass			
							# @RUSHY will handle OR 				
							# regular course entry					
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
					t = key["type"]
					name = key.get("name", t.replace('-', ' ').title())
					number = key["number"]
					notes = key["notes"] # not all data has this
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=certificate)
					req.save()
					# add courses via loop, req.courses.add(course)
					for c in key["courses"]:
							# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
							m = re.match(r"^([A-Z]{3}) ?>= ?([0-9]{3})$", c)
							if m:
								dept = m.group(1)
								at_least = int(m.group(2))
								satisfied = Course.objects.filter(department=dept, number__gte=n)
								req.courses.add(satisfied)
							# DEPT* shortcut
							m = re.match(r"^([A-Z]{3})(\*)$", c)
							if m:
								dept = m.group(1)
								satisfied = Course.objects.filter(department=dept)
								req.courses.add(satisfied)							
							# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
							m = re.match(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$", c)
							if m:
								dept = m.group(1)
								area = m.group(2)
								at_least = int(m.group(3))
								satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
								req.courses.add(satisfied)
							# * shortcut
							m = re.match(r"^(\*)$", c)
							if m:
								satisfied = Course.objects.all()
								req.courses.add(satisfied)		
							# *>=NUMBER
							m = re.match(r"^\* ?>= ?([0-9]{3})$", c)
							if m:
								at_least = int(m.group(1))
								satisfied = Course.objects.filter(number__gte=n)
								req.courses.add(satisfied)						
							# special
							m = re.match(r"^special$", c)
							if m:
								pass					
							# theme:something
							m = re.match(r"^theme:", c)
							if m:
								pass			
							# @RUSHY will handle OR 				
							# regular course entry					
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
					t = key["type"]
					name = key.get("name", t.replace('-', ' ').title())
					number = key["number"]
					notes = key["notes"] # not all data has this
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=degree)
					req.save()
					# add courses via loop, req.courses.add(course)
					for c in key["courses"]:
						# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
						m = re.match(r"^([A-Z]{3}) ?>= ?([0-9]{3})$", c)
						if m:
							dept = m.group(1)
							at_least = int(m.group(2))
							satisfied = Course.objects.filter(department=dept, number__gte=n)
							req.courses.add(satisfied)
						# DEPT* shortcut
						m = re.match(r"^([A-Z]{3})(\*)$", c)
						if m:
							dept = m.group(1)
							satisfied = Course.objects.filter(department=dept)
							req.courses.add(satisfied)							
						# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
						m = re.match(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$", c)
						if m:
							dept = m.group(1)
							area = m.group(2)
							at_least = int(m.group(3))
							satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
							req.courses.add(satisfied)
						# * shortcut
						m = re.match(r"^(\*)$", c)
						if m:
							satisfied = Course.objects.all()
							req.courses.add(satisfied)		
						# *>=NUMBER
						m = re.match(r"^\* ?>= ?([0-9]{3})$", c)
						if m:
							at_least = int(m.group(1))
							satisfied = Course.objects.filter(number__gte=n)
							req.courses.add(satisfied)						
						# special
						m = re.match(r"^special$", c)
						if m:
							pass					
						# theme:something
						m = re.match(r"^theme:", c)
						if m:
							pass			
						# DEPT | etc -> ignore everything except first department
						m = re.match(r"^([A-Z]{3}) ? |", c)
						if m:
							dept = m.group(1)
							satisfied = Course.objects.filter(department=dept)
							req.courses.add(satisfied)
						# DEPT NUMBER | etc -> ignore everything except first department
						m = re.match(r"^(([A-Z]{3}) ([0-9]{3})([A-Z]+) |)", c)
						if m:
							dept = m.group(1)
							number = m.group(2)
							letter = m.group(3)
							satisfied = Course.objects.filter(department=dept, number=number, letter=letter)
							req.courses.add(satisfied)
						# regular course entry					
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