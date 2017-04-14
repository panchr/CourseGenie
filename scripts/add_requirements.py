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

			req = Requirement(name=name, t=t, number=number, notes=notes, parent=degree, intrinsic_score=intrinsic_score)
			req.save()
			# add courses via loop, req.courses.add(course)
			for c in key["courses"]:
				enter_course(c)

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
					intrinsic_score = k["score"]

					req = Requirement(name=name, t=t, number=number, notes=notes, parent=track, intrinsic_score=intrinsic_score)
					req.save()
					# add courses via loop
					for c in k["courses"]:
						enter_course(c)
				
		# add requirements that belong to the major
		for key in maj["requirements"]:
			t = key["type"]
			name = key.get("name", t.replace('-', ' ').title())
			number = key["number"]
			notes = key.get("notes", "")
			intrinsic_score = key["score"]

			req = Requirement(name=name, t=t, number=number, notes=notes, parent=major, intrinsic_score=intrinsic_score)
			req.save()
			# add courses via loop, req.courses.add(course)
			for c in key["courses"]:
				enter_course(c)			

entry = raw_data["certificates"]
for cert in entry:
	name = cert["name"]
	test = cert["name"]
	try:
		certificate = Certificate.objects.get(name=name)
		# print "found existing certificate " + name
	except Certificate.DoesNotExist:
		short_name = cert["short_name"]
		certificate = Certificate(name=name, short_name=short_name)
		certificate.save()
		# print "just created certificate " + short_name
				
		# add requirements that belong to the certificate
		if "requirements" in cert:
			for key in cert["requirements"]:
				t = key["type"]
				name = key.get("name", t.replace('-', ' ').title())
				number = key["number"]
				notes = key.get("notes", "")
				intrinsic_score = key["score"]

				# print "about to create " + name
				req = Requirement(name=name, t=t, number=number, notes=notes, parent=certificate, intrinsic_score=intrinsic_score)
				req.save()
				# add courses via loop, req.courses.add(course)
				for c in key["courses"]:
					enter_course(c)

def enter_course(c):
	# DEPT>=NUMBER shortcut, REMOVE SPACES BEFORE PARSING
	m = case1.match(c)
	if m:
		dept = m.group(1)
		n = int(m.group(2))
		satisfied = Course.objects.filter(department=dept, number__gte=n)
		for s in satisfied:
			req.courses.add(s)
		continue
	# DEPT* shortcut
	m = case2.match(c)
	if m:
		dept = m.group(1)
		satisfied = Course.objects.filter(department=dept)
		for s in satisfied:
			req.courses.add(s)	
		continue						
	# DEPT[AREA]>=NUMBER, REMOVE SPACES BEFORE PARSING
	m = case3.match(c)
	if m:
		dept = m.group(1)
		area = m.group(2)
		n = int(m.group(3))
		satisfied = Course.objects.filter(department=dept, area=area, number__gte=n)
		for s in satisfied:
			req.courses.add(s)
		continue
	# * shortcut
	m = case4.match(c)
	if m:
		satisfied = Course.objects.all()
		for s in satisfied:
			req.courses.add(s)	
		continue
	# *>=NUMBER
	m = case5.match(c)
	if m:
		n = int(m.group(1))
		satisfied = Course.objects.filter(number__gte=n)
		for s in satisfied:
			req.courses.add(s)	
		continue
	# special
	m = case6.match(c)
	if m:
		continue
	# theme:something
	m = case7.match(c)
	if m:
		continue	
	# DEPT NUM | etc: put in the courses into nested requirement
	m = case8.match(c)
	if m:
		nested_req = NestedReq(requirement=req, number=1)
		nested_req.save()
		print "created nested cert req for " + req.name
		separated = map(str.strip, c.split("|"))
		for part in separated:
			part = part.strip()
			broken = part.split()
			if len(broken) >= 2:
				dept = broken[0]
				num = int(broken[1][:3])
				letter = ""
				if len(broken[1]) == 4:
					letter = broken[1][3]

				try: 
					course = Course.objects.get(department=dept, number=num, letter=letter)
					nested_req.courses.add(course)
				except Course.DoesNotExist:
					try:
						crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
						nested_req.courses.add(crossed.course)
					except CrossListing.DoesNotExist:
						pass
		continue						
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
				pass
		continue

			