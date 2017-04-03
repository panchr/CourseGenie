# scripts/add_requirements.py
# CourseGenie
# Author: Kathy Fan
# Date: March 31st, 2017
# Description: script to help add major and requirements data into database.

import sys
import os
if os.path.dirname(os.getcwd()) == 'scripts':
	os.chdir('..')
	sys.path.append(os.path.abspath('..'))
else:
	sys.path.append(os.path.abspath('.'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursegenie.settings")
import django
import json
import yaml
django.setup()
import re

from core.models import *

with open("data/all.yaml") as f:
	raw_data = yaml.load(f)

entry = raw_data["degrees"]
for deg in entry:
	name = deg["name"]
	try:
		degree = Degree.objects.get(name=name)
	except Degree.DoesNotExist:
		short_name = deg["short_name"]
		degree = Degree(name=name, short_name=short_name)
		degree.save()
			
		# add requirements that belong to the degree
		for key in deg["requirements"]:
			t = key["type"]
			name = key.get("name", t.replace('-', ' ').title())
			number = key["number"]
			notes = key.get("notes", "")
			req = Requirement(name=name, t=t, number=number, notes=notes, parent=degree)
			req.save()
			# add courses via loop, req.courses.add(course)
			for c in key["courses"]:
				# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
				m = re.match(r"^([A-Z]{3}) ?>= ?([0-9]{3})$", c)
				if m:
					dept = m.group(1)
					n = int(m.group(2))
					satisfied = Course.objects.filter(department=dept, number__gte=n)
					req.courses.add(satisfied, bulk=True)
				# DEPT* shortcut
				m = re.match(r"^([A-Z]{3})(\*)$", c)
				if m:
					dept = m.group(1)
					satisfied = Course.objects.filter(department=dept)
					req.courses.add(satisfied, bulk=True)							
				# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
				m = re.match(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$", c)
				if m:
					dept = m.group(1)
					area = m.group(2)
					n = int(m.group(3))
					satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
					req.courses.add(satisfied, bulk=True)
				# * shortcut
				m = re.match(r"^(\*)$", c)
				if m:
					satisfied = Course.objects.all()
					req.courses.add(satisfied, bulk=True)		
				# *>=NUMBER
				m = re.match(r"^\* ?>= ?([0-9]{3})$", c)
				if m:
					n = int(m.group(1))
					satisfied = Course.objects.filter(number__gte=n)
					req.courses.add(satisfied, bulk=True)						
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
					req.courses.add(satisfied, bulk=True)
				# DEPT NUMBER | etc -> ignore everything except first department
				m = re.match(r"^(([A-Z]{3}) ([0-9]{3})([A-Z]+) |)", c)
				if m:
					dept = m.group(1)
					number = m.group(2)
					letter = m.group(3)
					satisfied = Course.objects.filter(department=dept, number=number, letter=letter)
					req.courses.add(satisfied, bulk=True)
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
						print "could not find a course"	
entry = raw_data["majors"]		
for maj in entry:
	name = maj["name"]
	try:
		major = Major.objects.get(name=name)
	except Major.DoesNotExist:
		short_name = maj["short_name"]
		degree = Degree.objects.get(short_name=maj["degree"])
		major = Major(name=name, short_name=short_name, degree=degree)
		major.save()
				
		# add tracks
		if "tracks" in maj:
			for key in maj["tracks"]:
				name = key
				track = Track(major=major, name=name)
				track.save()
				for k in maj["tracks"][key]:
					t = k["type"]
					name = k.get("name", t.replace('-', ' ').title())
					number = k["number"]
					notes = k.get("notes", "")
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=track)
					req.save()
					# add courses via loop, req.courses.add(course)
					for c in k["courses"]:
						# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
						m = re.match(r"^([A-Z]{3}) ?>= ?([0-9]{3})$", c)
						if m:
							dept = m.group(1)
							n = int(m.group(2))
							satisfied = Course.objects.filter(department=dept, number__gte=n)
							for s in satisfied:
								req.courses.add(s)
						# DEPT* shortcut
						m = re.match(r"^([A-Z]{3})(\*)$", c)
						if m:
							dept = m.group(1)
							satisfied = Course.objects.filter(department=dept)
							req.courses.add(satisfied, bulk=True)							
						# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
						m = re.match(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$", c)
						if m:
							dept = m.group(1)
							area = m.group(2)
							n = int(m.group(3))
							satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
							for s in satisfied:
								req.courses.add(s)
						# * shortcut
						m = re.match(r"^(\*)$", c)
						if m:
							satisfied = Course.objects.all()
							req.courses.add(satisfied, bulk=True)		
						# *>=NUMBER
						m = re.match(r"^\* ?>= ?([0-9]{3})$", c)
						if m:
							n = int(m.group(1))
							satisfied = Course.objects.filter(number__gte=n)
							for s in satisfied:
								req.courses.add(s)						
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
							for s in satisfied:
								req.courses.add(s)
						# DEPT NUMBER | etc -> ignore everything except first department
						m = re.match(r"^(([A-Z]{3}) ([0-9]{3})([A-Z]+) |)", c)
						if m:
							dept = m.group(1)
							number = m.group(2)
							letter = m.group(3)
							satisfied = Course.objects.filter(department=dept, number=number, letter=letter)
							for s in satisfied:
								req.courses.add(s)			
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
								print "could not find a course"	
				
		# add requirements that belong to the major
		for key in maj["requirements"]:
			t = key["type"]
			name = key.get("name", t.replace('-', ' ').title())
			number = key["number"]
			notes = key.get("notes", "")
			req = Requirement(name=name, t=t, number=number, notes=notes, parent=major)
			req.save()
			# add courses via loop, req.courses.add(course)
			for c in key["courses"]:
				# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
				m = re.match(r"^([A-Z]{3}) ?>= ?([0-9]{3})$", c)
				if m:
					dept = m.group(1)
					n = int(m.group(2))
					satisfied = Course.objects.filter(department=dept, number__gte=n)
					for s in satisfied:
						req.courses.add(s)
				# DEPT* shortcut
				m = re.match(r"^([A-Z]{3})(\*)$", c)
				if m:
					dept = m.group(1)
					satisfied = Course.objects.filter(department=dept)
					for s in satisfied:
						req.courses.add(s)						
				# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
				m = re.match(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$", c)
				if m:
					dept = m.group(1)
					area = m.group(2)
					n = int(m.group(3))
					satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
					for s in satisfied:
						req.courses.add(s)
				# * shortcut
				m = re.match(r"^(\*)$", c)
				if m:
					satisfied = Course.objects.all()
					for s in satisfied:
						req.courses.add(s)		
				# *>=NUMBER
				m = re.match(r"^\* ?>= ?([0-9]{3})$", c)
				if m:
					n = int(m.group(1))
					satisfied = Course.objects.filter(number__gte=n)
					for s in satisfied:
						req.courses.add(s)					
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
					for s in satisfied:
						req.courses.add(s)
				# DEPT NUMBER | etc -> ignore everything except first department
				m = re.match(r"^(([A-Z]{3}) ([0-9]{3})([A-Z]+) |)", c)
				if m:
					dept = m.group(1)
					number = m.group(2)
					letter = m.group(3)
					satisfied = Course.objects.filter(department=dept, number=number, letter=letter)
					for s in satisfied:
						req.courses.add(s)			
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
						print "could not find a course"				

entry = raw_data["certificates"]
for cert in entry:
	name = cert["name"]
	try:
		certificate = Certificate.objects.get(name=name)
	except Certificate.DoesNotExist:
		short_name = cert["short_name"]
		certificate = Certificate(name=name, short_name=short_name)
		certificate.save()
				
		# add requirements that belong to the certificate
		if "requirements" in cert:
			for key in cert["requirements"]:
				t = key["type"]
				name = key.get("name", t.replace('-', ' ').title())
				number = key["number"]
				notes = key.get("notes", "")
				req = Requirement(name=name, t=t, number=number, notes=notes, parent=certificate)
				req.save()
				# add courses via loop, req.courses.add(course)
				for c in key["courses"]:
					# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
					m = re.match(r"^([A-Z]{3}) ?>= ?([0-9]{3})$", c)
					if m:
						dept = m.group(1)
						n = int(m.group(2))
						satisfied = Course.objects.filter(department=dept, number__gte=n)
						for s in satisfied:
							req.courses.add(s)
						break
					# DEPT* shortcut
					m = re.match(r"^([A-Z]{3})(\*)$", c)
					if m:
						dept = m.group(1)
						satisfied = Course.objects.filter(department=dept)
						for s in satisfied:
							req.courses.add(s)	
						break						
					# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
					m = re.match(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$", c)
					if m:
						dept = m.group(1)
						area = m.group(2)
						n = int(m.group(3))
						satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
						for s in satisfied:
							req.courses.add(s)
						break
					# * shortcut
					m = re.match(r"^(\*)$", c)
					if m:
						satisfied = Course.objects.all()
						for s in satisfied:
							req.courses.add(s)	
						break
					# *>=NUMBER
					m = re.match(r"^\* ?>= ?([0-9]{3})$", c)
					if m:
						n = int(m.group(1))
						satisfied = Course.objects.filter(number__gte=n)
						for s in satisfied:
							req.courses.add(s)	
						break				
					# special
					m = re.match(r"^special$", c)
					if m:
						break					
					# theme:something
					m = re.match(r"^theme:", c)
					if m:
						break			
					# DEPT | etc -> ignore everything except first department
					m = re.match(r"^([A-Z]{3}) ? |", c)
					if m:
						dept = m.group(1)
						satisfied = Course.objects.filter(department=dept)
						for s in satisfied:
							req.courses.add(s)
						break
					# DEPT NUMBER | etc -> ignore everything except first department
					m = re.match(r"^(([A-Z]{3}) ([0-9]{3})([A-Z]+) |)", c)
					if m:
						dept = m.group(1)
						number = m.group(2)
						letter = m.group(3)
						satisfied = Course.objects.filter(department=dept, number=number, letter=letter)
						for s in satisfied:
							req.courses.add(s)	
						break			
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
							print "could not find a course"	

			