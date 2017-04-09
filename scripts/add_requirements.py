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

case1 = re.compile(r"^([A-Z]{3}) ?>= ?([0-9]{3})$") 
case2 = re.compile(r"^([A-Z]{3})(\*)$")
case3 = re.compile(r"^([A-Z]{3})\[([A-Z]+)\] ?>= ?([0-9]{3})$")
case4 = re.compile(r"^(\*)$")
case5 = re.compile(r"^\* ?>= ?([0-9]{3})$")
case6 = re.compile(r"^special")
case7 = re.compile(r"^theme:")
case8 = re.compile(r"^([A-Z]{3}) ([0-9]{3})([A-Z]?) | .*")
case9 = re.compile(r"^([A-Z]{3}) ([0-9]{3})([A-Z]?)")

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
			intrinsic_score = key["score"]
			'''
			try:
				#req = Requirement.objects.get(name=name, t=t, number=number, notes=notes, parent=degree)
				req = Requirement.objects.get(object_id=requirements.id, object_ct=ContentType.objects.get_for_model(requirements))
			except Requirement.DoesNotExist:
				req = Requirement(name=name, t=t, number=number, notes=notes, parent=degree)
				req.save()
			'''
			req = Requirement(name=name, t=t, number=number, notes=notes, parent=degree, intrinsic_score=intrinsic_score)
			req.save()
			# add courses via loop, req.courses.add(course)
			for c in key["courses"]:
				# DEPT>=NUMBER shortcut
				m = case1.match(c)
				if m:
					dept = m.group(1)
					n = int(m.group(2))
					satisfied = Course.objects.filter(department=dept, number__gte=n)
					for s in satisfied:
						req.courses.add(s)
					break
				# DEPT* shortcut
				m = case2.match(c)
				if m:
					dept = m.group(1)
					satisfied = Course.objects.filter(department=dept)
					for s in satisfied:
						req.courses.add(s)
					break							
				# DEPT[AREA]>=NUMBER
				m = case3.match(c)
				if m:
					dept = m.group(1)
					area = m.group(2)
					n = int(m.group(3))
					satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
					for s in satisfied:
						req.courses.add(s)
					break
				# * shortcut # possibly with optional quote marks
				m = case4.match(c)
				if m:
					satisfied = Course.objects.all()
					for s in satisfied:
						req.courses.add(s)	
					break	
				# *>=NUMBER
				m = case5.match(c)
				if m:
					n = int(m.group(1))
					satisfied = Course.objects.filter(number__gte=n)
					for s in satisfied:
						req.courses.add(s)	
					break					
				# special
				m = case6.match(c)
				if m:
					break					
				# theme:something
				m = case7.match(c)
				if m:
					break			
				# DEPT NUM | etc: put in the courses into nested requirement
				m = case8.match(c)
				if m:
					m = m.group(0)
					nested_req = NestedReq(requirement=req, number=1)
					separated = m.split("|")
					for part in separated:
						part = part.strip()
						
						dept = part.split()[0]
						num = part.split()[1][:3]
						letter = ""
						if len(part.split()[1]) == 4:
							letter = part.split()[1][3]

						try: 
							course = Course.objects.get(department=dept, number=num, letter=letter)
							nested_req.courses.add(course)
						except Course.DoesNotExist:
							try:
								crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
								nested_req.courses.add(crossed.course)
							except CrossListing.DoesNotExist:
								pass
					break

				# regular course entry	
				m = case9.match(c)
				if m:			
					dept = m.group(1)
					numb = m.group(2)
					letter = m.group(3)
					try: # in case course isn't in database
						course = Course.objects.get(department=dept, number=num, letter=letter) 
						req.courses.add(course)
					except Course.DoesNotExist: # either actually not in database, or is a cross listing
						try:
							crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
							req.courses.add(crossed.course)
						except CrossListing.DoesNotExist:
							# do something to tell us c was not added	
							pass	

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
				try:
					track = Track.objects.get(major=major, name=name)
				except Track.DoesNotExist:
					track = Track(major=major, name=name)
					track.save()
				for k in maj["tracks"][key]:
					t = k["type"]
					name = k.get("name", t.replace('-', ' ').title())
					number = k["number"]
					notes = k.get("notes", "")
					intrinsic_score = key["score"]
					'''
					try:
						#req = Requirement.objects.get(name=name, t=t, number=number, notes=notes, parent=track)
						req = Requirement.objects.get(object_id=requirements.id, object_ct=ContentType.objects.get_for_model(requirements))
					except Requirement.DoesNotExist:
						req = Requirement(name=name, t=t, number=number, notes=notes, parent=track)
						req.save()
					'''
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=track, intrinsic_score=intrinsic_score)
					req.save()
					# add courses via loop
					for c in k["courses"]:
						# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
						m = case1.match(c)
						if m:
							dept = m.group(1)
							n = int(m.group(2))
							satisfied = Course.objects.filter(department=dept, number__gte=n)
							for s in satisfied:
								req.courses.add(s)
							break
						# DEPT* shortcut
						m = case2.match(c)
						if m:
							dept = m.group(1)
							satisfied = Course.objects.filter(department=dept)
							for s in satisfied:
								req.courses.add(s)	
							break					
						# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
						m = case3.match(c)
						if m:
							dept = m.group(1)
							area = m.group(2)
							n = int(m.group(3))
							satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
							for s in satisfied:
								req.courses.add(s)
							break
						# * shortcut
						m = case4.match(c)
						if m:
							satisfied = Course.objects.all()
							for s in satisfied:
								req.courses.add(s)
							break	
						# *>=NUMBER
						m = case5.match(c)
						if m:
							n = int(m.group(1))
							satisfied = Course.objects.filter(number__gte=n)
							for s in satisfied:
								req.courses.add(s)	
							break					
						# special
						m = case6.match(c)
						if m:
							break					
						# theme:something
						m = case7.match(c)
						if m:
							break			
						# DEPT NUM | etc: put in the courses into nested requirement
						m = case8.match(c)
						if m:
							m = m.group(0)
							nested_req = NestedReq(requirement=req, number=1)
							separated = m.split("|")
							for part in separated:
								part = part.strip()
								
								dept = part.split()[0]
								num = part.split()[1][:3]
								letter = ""
								if len(part.split()[1]) == 4:
									letter = part.split()[1][3]

								try: 
									course = Course.objects.get(department=dept, number=num, letter=letter)
									nested_req.courses.add(course)
								except Course.DoesNotExist:
									try:
										crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
										nested_req.courses.add(crossed.course)
									except CrossListing.DoesNotExist:
										pass
							break		
						# regular course entry	
						m = case9.match(c)
						if m:			
							dept = m.group(1)
							num = m.group(2)
							letter = m.group(3)
							try: # in case course isn't in database
								course = Course.objects.get(department=dept, number=num, letter=letter) 
								req.courses.add(course)
							except Course.DoesNotExist: # either actually not in database, or is a cross listing
								try:
									crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
									req.courses.add(crossed.course)
								except CrossListing.DoesNotExist:
									# do something to tell us c was not added	
									pass	
				
		# add requirements that belong to the major
		for key in maj["requirements"]:
			t = key["type"]
			name = key.get("name", t.replace('-', ' ').title())
			number = key["number"]
			notes = key.get("notes", "")
			intrinsic_score = key["score"]
			'''
			try:
				#req = Requirement.objects.get(name=name, t=t, number=number, notes=notes, parent=major)
				req = Requirement.objects.get(object_id=requirements.id, object_ct=ContentType.objects.get_for_model(requirements))
			except:
				req = Requirement(name=name, t=t, number=number, notes=notes, parent=major)
				req.save()
			'''
			req = Requirement(name=name, t=t, number=number, notes=notes, parent=major, intrinsic_score=intrinsic_score)
			req.save()
			# add courses via loop, req.courses.add(course)
			for c in key["courses"]:
				# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
				m = case1.match(c)
				if m:
					dept = m.group(1)
					n = int(m.group(2))
					satisfied = Course.objects.filter(department=dept, number__gte=n)
					for s in satisfied:
						req.courses.add(s)
					break
				# DEPT* shortcut
				m = case2.match(c)
				if m:
					dept = m.group(1)
					satisfied = Course.objects.filter(department=dept)
					for s in satisfied:
						req.courses.add(s)	
					break					
				# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
				m = case3.match(c)
				if m:
					dept = m.group(1)
					area = m.group(2)
					n = int(m.group(3))
					satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
					for s in satisfied:
						req.courses.add(s)
					break
				# * shortcut
				m = case4.match(c)
				if m:
					satisfied = Course.objects.all()
					for s in satisfied:
						req.courses.add(s)	
					break	
				# *>=NUMBER
				m = case5.match(c)
				if m:
					n = int(m.group(1))
					satisfied = Course.objects.filter(number__gte=n)
					for s in satisfied:
						req.courses.add(s)	
					break				
				# special
				m = case6.match(c)
				if m:
					break					
				# theme:something
				m = case7.match(c)
				if m:
					break			
				# DEPT NUM | etc: put in the courses into nested requirement
				m = case8.match(c)
				if m:
					m = m.group(0)
					nested_req = NestedReq(requirement=req, number=1)
					separated = m.split("|")
					for part in separated:
						part = part.strip()
						
						dept = part.split()[0]
						num = part.split()[1][:3]
						letter = ""
						if len(part.split()[1]) == 4:
							letter = part.split()[1][3]

						try: 
							course = Course.objects.get(department=dept, number=num, letter=letter)
							nested_req.courses.add(course)
						except Course.DoesNotExist:
							try:
								crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
								nested_req.courses.add(crossed.course)
							except CrossListing.DoesNotExist:
								pass
					break		
				# regular course entry	
				m = case9.match(c)
				if m:			
					dept = m.group(1)
					num = m.group(2)
					letter = m.group(3)
					try: # in case course isn't in database
						course = Course.objects.get(department=dept, number=num, letter=letter) 
						req.courses.add(course)
					except Course.DoesNotExist: # either actually not in database, or is a cross listing
						try:
							crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
							req.courses.add(crossed.course)
						except CrossListing.DoesNotExist:
							# do something to tell us c was not added	
							pass			

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
				intrinsic_score = key["score"]
				'''
				try:
					#req = Requirement.objects.get(name=name, t=t, number=number, notes=notes, parent=certificate)
					req = Requirement.objects.get(object_id=requirements.id, object_ct=ContentType.objects.get_for_model(requirements))
				except Requirement.DoesNotExist:
					req = Requirement(name=name, t=t, number=number, notes=notes, parent=certificate)
					req.save()
				'''
				req = Requirement(name=name, t=t, number=number, notes=notes, parent=certificate, intrinsic_score=intrinsic_score)
				req.save()
				# add courses via loop, req.courses.add(course)
				#print name #for debugging purposes
				for c in key["courses"]:
					# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
					m = case1.match(c)
					if m:
						dept = m.group(1)
						n = int(m.group(2))
						satisfied = Course.objects.filter(department=dept, number__gte=n)
						for s in satisfied:
							req.courses.add(s)
						break
					# DEPT* shortcut
					m = case2.match(c)
					if m:
						dept = m.group(1)
						satisfied = Course.objects.filter(department=dept)
						for s in satisfied:
							req.courses.add(s)	
						break						
					# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
					m = case3.match(c)
					if m:
						dept = m.group(1)
						area = m.group(2)
						n = int(m.group(3))
						satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
						for s in satisfied:
							req.courses.add(s)
						break
					# * shortcut
					m = case4.match(c)
					if m:
						satisfied = Course.objects.all()
						for s in satisfied:
							req.courses.add(s)	
						break
					# *>=NUMBER
					m = case5.match(c)
					if m:
						n = int(m.group(1))
						satisfied = Course.objects.filter(number__gte=n)
						for s in satisfied:
							req.courses.add(s)	
						break				
					# special
					m = case6.match(c)
					if m:
						break					
					# theme:something
					m = case7.match(c)
					if m:
						break			
					# DEPT NUM | etc: put in the courses into nested requirement
					m = case8.match(c)
					if m:
						m = m.group(0)
						nested_req = NestedReq(requirement=req, number=1)
						separated = m.split("|")
						for part in separated:
							part = part.strip()
							print "part is " + part
							dept = part.split()[0]
							num = part.split()[1][:3]
							letter = ""
							if len(part.split()[1]) == 4:
								letter = part.split()[1][3]

							try: 
								course = Course.objects.get(department=dept, number=num, letter=letter)
								nested_req.courses.add(course)
							except Course.DoesNotExist:
								try:
									crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
									nested_req.courses.add(crossed.course)
								except CrossListing.DoesNotExist:
									pass
						break		
					# regular course entry	
					m = case9.match(c)
					if m:			
						dept = m.group(1)
						num = m.group(2)
						letter = m.group(3)
						try: # in case course isn't in database
							course = Course.objects.get(department=dept, number=num, letter=letter) 
							req.courses.add(course)
						except Course.DoesNotExist: # either actually not in database, or is a cross listing
							try:
								crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
								req.courses.add(crossed.course)
							except CrossListing.DoesNotExist:
								# do something to tell us c was not added	
								pass

			