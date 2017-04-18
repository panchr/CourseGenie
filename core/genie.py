# -*- coding: utf-8 -*-
# core/genie.py
# CourseGenie
# Author: Kathy Fan
# Date: April 5th, 2017
# functions related to profiles

import json
import re
import random

from django.db import transaction

from core.models import *

RANK_D = 36 # degree
RANK_M = 33 # major
RANK_T = 20 # track
RANK_C = 22 # certificate
RANK_WLD = 10 # white listed department
RANK_WLA = 10 # white listed area
RANK_BLD = 10 # black listed department
RANK_BLA = 10 # black listed area
RANK_F = 3 # flexibility; other BSE majors
RANK_A = 5 # untaken distribution area
TOP_COUNT = 20
DISTRO_AREA_REQ = Requirement.objects.get(t="distribution-areas", number=4)

# store user records for manual input of courses
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

# calculate all progresses corresponding to a calendar
def calculate_progress(calendar):
	profile = calendar.profile
	list_courses = []

	Progress.objects.filter(calendar=calendar).delete() # delete old ones, start from scratch

	for record in Record.objects.filter(profile=calendar.profile).prefetch_related('course'):
		list_courses.append(record.course)
	
	# degree requirements
	print "now doing degree"
	calculate_single_progress(calendar, calendar.degree, list_courses)

	# requirements of major itself
	print "now doing major"
	calculate_single_progress(calendar, calendar.major, list_courses)

	# track requirements, if any
	track = calendar.track
	if track != None:
		calculate_single_progress(calendar, track, list_courses)

	# certificates requirements, if any number
	for certificate in calendar.certificates.all():
		calculate_single_progress(calendar, certificate, list_courses)

# calculate for one single degree/major/track/certificate; to be called from calculate_progress
# NEED TO DEBUG
def calculate_single_progress(calendar, category, list_courses):
	FACTOR = 5
	number_choices = [] # number of courses to choose from for this requirement
	number_remaining = [] # number of courses left to fulfill for this requirement
	other_than = [] # list of lists of nestedreq IDs that should no longer be considered
	c = 0 # count of number of choices
	nested_reqs = None
	list_progresses = []
	cat_requirements = category.requirements.all()
	for requirement in cat_requirements:
		number_remaining.append(requirement.number)
		c += requirement.courses.count()
		nested_reqs = requirement.nested_reqs.all()
		for nreq in nested_reqs:
			c += nreq.courses.count()
		if requirement == DISTRO_AREA_REQ:
			c = 800 # small hack... need this to be less than 880 of distribution-additional
		print requirement.name + " has " + str(c) # prints how many courses qualify under a requirement
		number_choices.append(c) 
		other_than.append([])
		c = 0

		# create default progresses for all requirements, with number_taken = 0, completed = False
		list_progresses.append(Progress(calendar=calendar, requirement=requirement))
	Progress.objects.bulk_create(list_progresses)

	for course in list_courses:
		print course.department + str(course.number) # prints the course
		matched = {}
		i = 0

		for requirement in cat_requirements:
			if course in requirement.courses.all():
				matched[i] = requirement

			nested_reqs = NestedReq.objects.filter(requirement=requirement).exclude(id__in=other_than[i])
			for nreq in nested_reqs:
				if course in nreq.courses.all():
					small_list = [nreq, requirement]
					matched[i] = small_list
			i += 1
	
		if len(matched) == 0: # course did not satisfy any requirements; no Progresses need to be updated
			pass

		elif len(matched) == 1: # course satisfied one requirement; need to update the progress
			index = 0
			req = None
			for key in matched: # there should only be one
				index = key
				found = False
				if isinstance(matched[key], Requirement):
					req = matched[key]
				if isinstance(matched[key], list):
					nreq = matched[key][0]
					req = matched[key][1]
					other_than.append(nreq.id)
				if req != None: # doesn't make sense that req would still be None though
					print req
					progress = Progress.objects.get(calendar=calendar, requirement=req)	
					progress.number_taken += 1
					progress.courses_taken.add(course)
					if progress.number_taken >= req.number and progress.completed == False:
						progress.completed = True
					progress.save()
					number_remaining[index] -= 1

		else: # course satisfied multiple requirements
			diff = []
			for j in range (0, len(number_choices)):
				#diff.append(number_choices[j])
				diff.append(number_choices[j] - number_remaining[j] * FACTOR)

			min_val = 1000000
			min_key = 0
			for key in matched:
				if diff[key] < min_val:
					min_val = diff[key]
					min_key = key

			if isinstance(matched[min_key], Requirement):
				req = matched[min_key]
			if isinstance(matched[min_key], list):
				nreq = matched[min_key][0]
				req = matched[min_key][1]
				other_than.append(nreq.id)			
			progress = Progress.objects.get(calendar=calendar, requirement=req)
			progress.number_taken += 1
			progress.courses_taken.add(course)
			if progress.number_taken >= req.number and progress.completed == False:
				progress.completed = True
			progress.save()
			number_remaining[min_key] -= 1

# the brains of the project!!!
# wow so much brains :o (all due to Rushy)
# IN PROGRESS
def _add_nested_courses(reqs):
	courses_list = {r: set(r.courses.all()) for r in reqs}
	for r in courses_list:
		for nested in NestedReq.objects.filter(requirement=r):
			courses_list[r] |= set(nested.courses.all())
	return courses_list

def _update_entry(filters, entry, requirements, req_courses, course, delta, fmt):
	SCALE = 40
	if delta == RANK_F: # flexibility needs to be weighed less
		SCALE = 20
	for req in requirements:
		if course in req_courses[req]:
			entry['score'] += delta + req.intrinsic_score * SCALE # base
			if delta == RANK_D:
				if req in filters: # add points for empty reqs for degree
					entry['score'] += 4
				if req == DISTRO_AREA_REQ:
					entry['score'] += random.randint(20, 30)
			if delta == RANK_M and req in filters: # add points for empty reqs for major
				entry['score'] += 4
			entry['reason'] += fmt.format(req.name)

def recommend(calendar):
	profile = calendar.profile
	major = calendar.major
	degree = calendar.degree
	random.seed(profile.user_id)

	user_progresses = Progress.objects.filter(calendar=calendar)
	if user_progresses.count() == 0:
		calculate_progress(calendar)

	progresses = user_progresses.filter(completed=True)
	satisfied_reqs = []
	for progress in progresses:
		satisfied_reqs.append(progress.requirement)

	zero_progresses = user_progresses.filter(number_taken=0)
	empty_reqs = []
	for progress in zero_progresses:
		empty_reqs.append(progress.requirement)

	degree_requirements = list(degree.requirements.exclude(id__in=[o.id for o in satisfied_reqs]))
	degree_req_courses = _add_nested_courses(degree_requirements)

	major_requirements = list(major.requirements.exclude(id__in=[o.id for o in satisfied_reqs]))
	major_req_courses = _add_nested_courses(major_requirements)

	track_requirements = []
	track_req_courses = {}
	if calendar.track:
		track_requirements = list(calendar.track.requirements.exclude(id__in=[o.id for o in satisfied_reqs]))
		track_req_courses = _add_nested_courses(track_requirements)

	certificates = {}
	for cert in calendar.certificates.all():
		certificates[cert] = [[], {}]
		cert_requirements = list(cert.requirements.exclude(id__in=[o.id for o in satisfied_reqs]))
		cert_req_courses = _add_nested_courses(cert_requirements)

		certificates[cert][0] = cert_requirements
		certificates[cert][1] = cert_req_courses

	other_majors = {}
	for maj in Major.objects.exclude(id=major.id):
		other_majors[maj] = [[], {}]
		maj_requirements = list(maj.requirements.all())
		maj_req_courses = _add_nested_courses(maj_requirements)

		other_majors[maj][0] = maj_requirements
		other_majors[maj][1] = maj_req_courses

	# filter out courses they've taken already
	filter_out = set(map(lambda r: r.course, profile.records.all().prefetch_related('course')))
	taken_areas = set(map(lambda x: x.area, filter_out))
 
 	# some courses don't have distribution requirements and so if this was not
 	# added as taken, those courses would get arbitrarily suggested.
	taken_areas.add("")

	# filter out courses already in calendar, no repeatss
	for semester in calendar.semesters.all().prefetch_related('courses'):
		filter_out |= set(semester.courses.all())

	wl_depts_short = set()
	wl_areas = set()
	bl_depts_short = set()
	bl_areas = set()
	try:
		preference = Preference.objects.get(profile=profile)
	except Preference.DoesNotExist:
		pass
	else:
		# filter out black listed courses, no repeats
		filter_out |= set(preference.bl_courses.all())
		wl_depts_short = set(preference.wl_depts.all().values_list('short_name', flat=True))
		wl_areas = set(preference.wl_areas.all().values_list('short_name', flat=True))
		bl_depts_short = set(preference.bl_depts.all().values_list('short_name', flat=True))
		bl_areas = set(preference.bl_areas.all().values_list('short_name', flat=True))

	list_suggestions = dict()
	# create list of all the courses. Each entry is a dictionary
	# [
	#	{
	#		'course_id': '123456', 
	#		'name': 'Macroeconomics', 
	#		'short_name': 'ECO 101A',
	#		'department': 'ECO',
	#		'number': 101,
	#		'letter': 'A',
	#		'reason': 'some string here', # build string before passing it in
	#		'score': 3
	#	}
	# ]
	for course in Course.objects.all():
		if course not in filter_out and course.pk not in list_suggestions:
			department = course.department
			area = course.area

			entry = {'course_id': course.course_id, 'name': course.name, 'department': department,
			'number': course.number, 'letter': course.letter, 'short_name': department + " " + str(course.number) + course.letter,
			'score': 0, 'reason': ""} 

			# add points if in wl_depts (primary department only)
			if department in wl_depts_short:
				entry['score'] += RANK_WLD

			# add points if in wl_areas
			if area in wl_areas:
				entry['score'] += RANK_WLA

			# subtract points if in bl_depts
			if department in bl_depts_short:
				entry['score'] -= RANK_BLD

			# subtract points if in bl_areas
			if area in bl_areas:
				entry['score'] -= RANK_BLA

			# add points if satisfy untaken area
			if area not in taken_areas:
				entry['score'] += RANK_A

			# add points if satisfy unsatisfied degree requirements
			_update_entry(empty_reqs, entry, degree_requirements, degree_req_courses, course,
				RANK_D,
				'{} requirement of your %s degree,\n' % degree.short_name)

			# add points if satisfy unsatisfied major requirements
			_update_entry(empty_reqs, entry, major_requirements, major_req_courses, course,
				RANK_M, '{} requirement of your %s major,\n' % major.short_name)

			# add points if satisfy unsatisfied track requirements
			if calendar.track is not None:
				_update_entry([], entry, track_requirements, track_req_courses, course,
					RANK_T, '{} requirement of your %s track,\n' % calendar.track.short_name)

			# for each certificate, add points if satisfy unsatisfied certificate requirements
			for cert in certificates:
				_update_entry([], entry, certificates[cert][0], certificates[cert][1][req],
				 	course, RANK_C,
					'{} requirement of your %s certificate,\n' % certificate.short_name)

			# add points if satisfy flexibility (requirements of other majors themselves, excluding their tracks)
			for maj in other_majors:
				_update_entry([], entry, other_majors[maj][0], other_majors[maj][1],
				 	course, RANK_F,
					'{} requirement of the %s major for flexibility,\n' % maj.short_name)

			if len(entry['reason']) > 1:
				entry['reason'] = "This course satisfies the " + entry['reason']
				entry['reason'] = entry['reason'][:-2] # take off last ,\n

			list_suggestions[course.id] = entry

	sorted_list = sorted(list_suggestions.values(), key=lambda k: k['score'],
		reverse=True)
	return sorted_list[:TOP_COUNT]
