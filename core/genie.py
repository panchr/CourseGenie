# core/genie.py
# CourseGenie
# Author: Kathy Fan
# Date: April 5th, 2017
# functions related to profiles

import json
import re

from django.db import transaction

from core.models import *

# store user's records for manual input of courses
# REQUESTED sample input from manual form:
# ["PHY 104", "WRI 105", "FRS 118", "ECO 101A"]
# BASICALLY FINISHED
# NEED TO CHANGE HOW TO ACCESS PROFILE
# MAY NEED TO CHECK: IF COURSE IS ALREADY IN TRANSCRIPT AND USER WAS STUPID
def store_manual(user, courses):
	list_records = []
	course_re = re.compile(r'^(?P<dept>[A-Z]{3}) (?P<num>\d{3})(?P<letter>[A-Z]?)$')
	profile = user.profile

	for item in courses:
		matches = course_re.match(item)
		if not matches:
			continue
		dept = matches.group('dept')
		num = matches.group('num')
		letter = matches.group('letter')
		try: # in case course isn't in database
			course = Course.objects.get(department=dept, number=num, letter=letter) 
			list_records.append(Record(course=course, profile=profile))
		except Course.DoesNotExist: # either actually not in database, or is a cross listing
			try:
				crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
				list_records.append(Record(course=crossed.course, profile=profile))
			except CrossListing.DoesNotExist:
				# do something to tell us c was not added	
				pass

	# This should be an atomic transaction so existing records are deleted
	# if and only if the new records are added in.
	with transaction.atomic():
		Record.objects.filter(profile=profile).delete()
		Record.objects.bulk_create(list_records)

# store rest of info from form: name, year, partial preferences (interests)
# from form_name: list of strings ['first name', 'last name', 'year']
# from form_interests: list of departments ['Economics', 'History', 'French']
# REQUESTED FORMAT FROM FRONT END ALREADY
# BASICALLY FINISHED
def store_rest_form(profile, form_name_input, departments):
	# parse form_name_input
	first_name = form_name_input[0]
	last_name = form_name_input[1]
	year = form_name_input[2]

	# add form_name_input parsed data 
	profile.user.first_name = first_name
	profile.user.last_name = last_name
	profile.year = year

	# does profile's Preference already exist?
	try: 
		pref = Preference.objects.get(profile=profile)
		pref.delete()

	except Preference.DoesNotExist:
		pass

	# now should be creating new Preference for profile
	pref = Preference(profile=profile)
	pref.save()

	for department in departments:
		try:
			dept = Department.objects.get(name=department)
			pref.wl_depts.add(dept)
		except Department.DoesNotExist:
			pass # just don't add it to wl_depts

# create a calendar. takes in:
# 	degree
# 	major
#	certificates: a list of certificates
# BASICALLY DONE
def create_calendar(profile, degree, major, certificates):
	calendar = Calendar(profile=profile, degree=degree, major=major)
	calendar.save()
	for certificate in certificates:
		calendar.certificates.add(certificate)

# update preferences of a profile (from magic lamp menu)
# ASK FRONTEND data format
# {
#	 'bl_courses': [],
#	 'bl_areas': [],
# 	 'bl_depts': [],
# 	 'wl_areas': [],
#	 'wl_depts': []
# }
# IN PROGRESS
def update_preferences(profile, raw_data):
	try:
		pref = Preference.objects.get(profile=profile)
		# find differences, update (instead of deleting and starting from scratch)

	except Preference.DoesNotExist:
		pref = Preference(profile=profile)
		pref.save()
		# add everything in

	pass

# calculate progress corresponding to a calendar
# a course already used to satisfy a requirement belonging to a particular degree/major/track/certificate
# should not be able to satisfy any other requirements under the same parent
# IN PROGRESS; needs planning before coding
def calculate_progress(calendar, requirement):
	profile = calendar.profile

	# degree requirements 
	degree = calendar.degree
	degree_requirements = Degree.requirements.all()
	for requirement in degree_requirements:
		progress = Progress(calendar=calendar, requirement=requirement)
		progress.save()

		number_taken = 0
		number_required = requirement.number
		course_choices = requirement.courses.all()
		for course in course_choices:
			try:
				record = Record.objects.get(profile=profile, course=course) # took this course
				number_taken += 1
				progress.courses.add(course)
			except Record.DoesNotExist: # did not take the course
				pass

		if number_taken >= number_required:		
			progress.completed = True

		progress.number_taken = number_taken

	# major requirements
	major = calendar.major
	major_requirements = Major.requirements.all() # should not include those of its tracks
	for requirement in major_requirements:
		pass
	# track requirements, if any

	# certificates requirements, if any number


# calculate for one certificate; to be called from calculate_progress
def calculate_progress_certificate():
	pass

# recommend courses from student's past courses, degree requirements, 
# major requirements, and certificate requirements
# IN PROGRESS; needs planning before coding
def recommend():
	# actual algorithm goes here
	list_suggestions = []
	# create list of all the courses 
	# [
	#	{
	#		'course_id': '123', 
	#		'name': 'Macroeconomics', 
	#		'short_name': 'ECO 101A',
	#		'department': 'ECO',
	#		'number': 101,
	#		'letter': 'A',
	#		'reason': 'some string here', # build string before passing it in
	#		'score': 3
	#	}
	# ]
	# how to deal with tracks within major? (How does user input this?)
	# should be removed from list if already in calendar
	return list_suggestions
