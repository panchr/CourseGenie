# -*- coding: utf-8 -*-
# core/genie.py
# CourseGenie
# Author: Kathy Fan
# Date: April 5th, 2017
# functions related to profiles

import json
import re

from django.utils import timezone
from django.db import transaction
from django.db.models import Count
from django.core.cache import cache

from core.models import *

RANK_D = 36 # degree
RANK_M = 33 # major
RANK_T = 20 # track
RANK_C = 22 # certificate
RANK_WLD = 10 # white listed department
RANK_WLA = 10 # white listed area
RANK_F = 3 # flexibility; other BSE majors
RANK_A = 5 # untaken distribution area
TOP_COUNT = 20

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
				pass

	# This should be an atomic transaction so existing records are deleted
	# if and only if the new records are added in.
	with transaction.atomic():
		Record.objects.filter(profile=profile).delete()
		Record.objects.bulk_create(list_records)

# store rest of info from form: name, year, partial preferences (interests)
# from form_name: list of strings ['first name', 'last name', 'year']
# from form_interests: list of departments ['Economics', 'History', 'French']
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
def create_calendar(profile, degree, major, certificates):
	calendar = Calendar(profile=profile, degree=degree, major=major)
	calendar.save()
	for certificate in certificates:
		calendar.certificates.add(certificate)

# calculate all progresses corresponding to a calendar
@transaction.atomic
def calculate_progress(calendar):
	profile = calendar.profile
	list_courses = []

	Progress.objects.filter(calendar=calendar, user_completed=False).delete() # delete old ones, start from scratch

	list_courses.extend(
		Record.objects.filter(profile=calendar.profile)
			.values_list('course_id', flat=True)
		)

	list_courses.extend(
		Semester.objects.filter(calendar=calendar)
			.values_list('courses', flat=True)
		)

	# degree requirements
	calculate_single_progress(calendar, calendar.degree, list_courses)

	# requirements of major itself
	calculate_single_progress(calendar, calendar.major, list_courses)

	# track requirements, if any
	track = calendar.track
	if track != None:
		calculate_single_progress(calendar, track, list_courses)

	# certificates requirements, if any number
	for certificate in calendar.certificates.all():
		calculate_single_progress(calendar, certificate, list_courses)

# calculate for one single degree/major/track/certificate; to be called from calculate_progress
def calculate_single_progress(calendar, category, list_courses):
	FACTOR = 5
	number_choices = [] # number of courses to choose from for this requirement
	number_remaining = [] # number of courses left to fulfill for this requirement
	other_than = [] # list of lists of nestedreq IDs that should no longer be considered
	c = 0 # count of number of choices
	nested_reqs = None
	progresses = {p.requirement: p for p in Progress.objects.filter(calendar=calendar, user_completed=True).select_related('requirement')}
	cat_requirements = list(category.requirements.all())

	req_courses = {r: set(r.courses.values_list('pk', flat=True)) for r in cat_requirements}
	nreq_courses = {r:
		{nr: set(nr.courses.values_list('pk', flat=True)) for nr in r.nested_reqs.all()}
		for r in cat_requirements}
	
	for requirement in cat_requirements:
		number_remaining.append(requirement.number)
		c += len(req_courses[requirement])
		# this is slower due to caching:
		# c += requirement.nested_reqs.aggregate(number=Count('courses')).get('number', 0)
		nested_reqs = nreq_courses[requirement]
		for nreq, cs in nested_reqs.items():
			c += len(cs)
		if requirement.t == 'distribution-areas':
			c = 800 # small hack... need this to be less than 880 of distribution-additional
		#print requirement.name + " has " + str(c) # prints how many courses qualify under a requirement
		number_choices.append(c) 
		other_than.append([])
		c = 0

		# create default progresses for all requirements, with number_taken = 0, completed = False
		if requirement not in progresses:
			p = Progress(calendar=calendar, requirement=requirement)
			progresses[requirement] = p

	progress_courses = {r: set() for r in progresses.keys()}
	Progress.objects.bulk_create(filter(lambda p: p.pk is None,
		progresses.values()))

	for course in list_courses:
		#print course.department + str(course.number) # prints the course
		matched = {}
		i = 0

		for requirement in cat_requirements:
			if course in req_courses[requirement]:
			#if course in requirement.courses.all().values_list('pk', flat=True):
				matched[i] = requirement

			# nested_reqs = NestedReq.objects.filter(requirement=requirement).exclude(id__in=other_than[i])
			for nreq, nreq_cs in nreq_courses[requirement].items():
				#if course in map(lambda x: x.pk, nreq.courses.all()):
				if nreq.pk in other_than[i]:
					continue
				if course in nreq_cs:
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
					#print req
					progress = progresses[req]
					if not (progress.completed or progress.user_completed):
						progress.number_taken += 1
						progress_courses[req].add(course)
						if progress.number_taken >= req.number and not progress.completed:
							progress.completed = True
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

			progress = progresses[req]
			if not (progress.completed or progress.user_completed):
				progress.number_taken += 1
				progress_courses[req].add(course)
				if progress.number_taken >= req.number and progress.completed == False:
					progress.completed = True
				number_remaining[min_key] -= 1

	for r, p in progresses.items():
		p.courses_taken.add(*progress_courses[r])
		p.save()

# the brains of the project!!!
# wow so much brains :o (all due to Rushy)
def _add_nested_courses(reqs):
	courses_list = {r: set(r.courses.all()) for r in reqs}
	for r in reqs:
		for nested in NestedReq.objects.filter(requirement=r):
			courses_list[r] |= set(nested.courses.all())
	return courses_list

def _update_entry(filters, entry, requirements, req_courses, course, delta, fmt, is_dist, short):
	SCALE = 40
	if delta == RANK_F: # flexibility needs to be weighed less
		SCALE = 20
	for req in requirements:
		if course in req_courses[req]:
			entry['score'] += delta + req.intrinsic_score * SCALE # base
			if delta == RANK_D:
				if req in filters: # add points for empty reqs for degree
					entry['score'] += 5
				#if req.t == 'distribution-areas':
				#	entry['score'] += random.randint(20, 35)
			if delta == RANK_M and req in filters: # add points for empty reqs for major
				entry['score'] += 4
			entry['reason'] += fmt.format(req.name)
			entry['reason_list'].append(short.format(req.name))

def recommend(calendar):
	cached_recs = get_cached_recommendation(calendar)
	if cached_recs is not None:
		return cached_recs

	profile = calendar.profile
	major = calendar.major
	degree = calendar.degree

	calculate_progress(calendar)
	user_progresses = Progress.objects.filter(calendar=calendar)

	progresses = user_progresses.filter(completed=True).select_related('requirement')
	satisfied_reqs = []
	for progress in progresses:
		satisfied_reqs.append(progress.requirement)

	progresses = user_progresses.filter(user_completed=True).select_related('requirement')
	satisfied_reqs = []
	for progress in progresses:
		satisfied_reqs.append(progress.requirement)

	zero_progresses = user_progresses.filter(number_taken=0).select_related('requirement')
	empty_reqs = []
	for progress in zero_progresses:
		empty_reqs.append(progress.requirement)

	degree_requirements = list(degree.requirements.exclude(id__in={o.id for o in satisfied_reqs}))
	degree_req_courses = _add_nested_courses(degree_requirements)

	major_requirements = list(major.requirements.exclude(id__in={o.id for o in satisfied_reqs}))
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
	filter_out = set(profile.records.all().values_list('course_id', flat=True))
	# filter_out = set(map(lambda r: r.course, profile.records.all().select_related('course')))

	# filter out courses already in calendar
	filter_out |= set(calendar.semesters.all().values_list('courses', flat=True))

	# filter out courses in sandbox
	filter_out |= set(calendar.sandbox.all())

	wl_depts_short = set()
	wl_areas = set()
	bl_depts_short = set()
	bl_areas = set()
	try:
		preference = Preference.objects.get(profile=profile)
	except Preference.DoesNotExist:
		pass
	else:
		# filter out black listed courses
		filter_out |= set(preference.bl_courses.all().values_list('pk', flat=True))
		wl_depts_short = set(preference.wl_depts.all().values_list('short_name', flat=True))
		wl_areas = set(preference.wl_areas.all().values_list('short_name', flat=True))
		bl_depts_short = set(preference.bl_depts.all().values_list('short_name', flat=True))
		bl_areas = set(preference.bl_areas.all().values_list('short_name', flat=True))

	list_suggestions_reg = dict()
	list_suggestions_dist = dict()
	# create list of all the courses. Each entry is a dictionary
	# [
	#	{
	#		'course': some course object, 
	#		'reason': 'some string here',
	#		'reason_list': ['string', 'string']
	#		'score': 3
	#	}
	# ]
	for course in Course.objects.all():
		if course.pk not in filter_out and course.pk not in list_suggestions_reg and course.pk not in list_suggestions_dist:
			department = course.department
			area = course.area

			entry = {'course': course, 'score': 0, 'reason': '', 'reason_list': []}

			# don't add blacklisted departments
			if department in bl_depts_short:
				continue

			# don't add blacklisted areas
			if area in bl_areas:
				continue

			# add points if in wl_depts (primary department only)
			if department in wl_depts_short:
				entry['score'] += RANK_WLD

			# add points if in wl_areas
			if area in wl_areas:
				entry['score'] += RANK_WLA

			is_dist = [0]
			# add points if satisfy unsatisfied degree requirements
			_update_entry(empty_reqs, entry, degree_requirements, degree_req_courses, course,
				RANK_D,
				'{} requirement of your %s degree,\n' % degree.short_name, is_dist,
				'%s {}' % degree.short_name)

			# add points if satisfy unsatisfied major requirements
			_update_entry(empty_reqs, entry, major_requirements, major_req_courses, course,
				RANK_M, '{} requirement of your %s major,\n' % major.short_name, is_dist,
				'%s {}' % major.short_name)

			# add points if satisfy unsatisfied track requirements
			if calendar.track is not None:
				_update_entry([], entry, track_requirements, track_req_courses, course,
					RANK_T, '{} requirement of your %s track,\n' % calendar.track.short_name, is_dist,
					'%s {}' % calendar.track.short_name)

			# for each certificate, add points if satisfy unsatisfied certificate requirements
			for cert in certificates:
				_update_entry([], entry, certificates[cert][0], certificates[cert][1],
				 	course, RANK_C,
					'{} requirement of your %s certificate,\n' % cert.short_name, is_dist,
					'%s {}' % cert.short_name)

			# add points if satisfy flexibility (requirements of other majors themselves, excluding their tracks)
			for maj in other_majors:
				_update_entry([], entry, other_majors[maj][0], other_majors[maj][1],
				 	course, RANK_F,
					'{} requirement of the %s major for flexibility,\n' % maj.short_name, is_dist,
					'%s {}' % maj.short_name)

			if len(entry['reason']) > 1:
				entry['reason'] = "This course satisfies the " + entry['reason']
				entry['reason'] = entry['reason'][:-2] # take off last ,\n

			if is_dist[0] == 1:
				list_suggestions_dist[course.id] = entry
			else:
				list_suggestions_reg[course.id] = entry

	sorted_reg = sorted(list_suggestions_reg.values(), key=lambda k: k['score'],
		reverse=True)

	sorted_dist = sorted(list_suggestions_dist.values(), key=lambda k: k['score'],
		reverse=True)

	sorted_total = []

	reg_length = len(sorted_reg)
	dist_length = len(sorted_dist)
	reg_times = reg_length / 3
	dist_times = dist_length
	marker = 0 # reg
	actual = min(reg_times, dist_times)
	if actual == dist_times:
		marker = 1 # dist

	for i in range(0, actual):
		sorted_total.extend(sorted_reg[3*i:3*i+3])
		sorted_total.append(sorted_dist[i])

	if marker == 0: # reg list was shorter
		sorted_total.extend(sorted_dist[actual:])

	if marker == 1:
		sorted_total.extend(sorted_reg[3*actual:])

	result = sorted_total[:TOP_COUNT]
	set_cached_recommendation(calendar, result)
	return result

def generate_semesters(calendar):
	grad_year = calendar.profile.year

	semesters = []

	now = timezone.now()
	if grad_year > now.year + 4:
		grad_year = now.year + 4
	if now.month in {1, 9, 10, 11, 12}: # SF SF ... S
		for y in range(now.year+1, grad_year):
			semesters.append(Semester(calendar=calendar, year=y, term=Semester.TERM_SPRING))
			semesters.append(Semester(calendar=calendar, year=y, term=Semester.TERM_FALL))
		semesters.append(Semester(calendar=calendar, year=grad_year, term=Semester.TERM_SPRING))

	else: # Spring or summer, F SF SF ... S
		semesters.append(Semester(calendar=calendar, year=now.year, term=Semester.TERM_FALL))
		for y in range(now.year+1, grad_year):
			semesters.append(Semester(calendar=calendar, year=y, term=Semester.TERM_SPRING))
			semesters.append(Semester(calendar=calendar, year=y, term=Semester.TERM_FALL))
		semesters.append(Semester(calendar=calendar,
			year=grad_year, term=Semester.TERM_SPRING))

	Semester.objects.bulk_create(semesters)

def _form_cache_key(calendar):
	return '%d-%d' % (calendar.profile_id, calendar.pk)

def get_cached_recommendation(calendar):
	return cache.get(_form_cache_key(calendar))

def set_cached_recommendation(calendar, recs):
	return cache.set(_form_cache_key(calendar), recs, timeout=15*60)

def clear_cached_recommendations(profile_id, calendar_id=None):
	if calendar_id is not None:
		return cache.delete('%d-%d' % (profile_id, calendar_id))
	else:
		return cache.delete_pattern('%d-*' % profile_id)
