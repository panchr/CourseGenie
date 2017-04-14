# core/genie.py
# CourseGenie
# Author: Kathy Fan
# Date: April 5th, 2017
# functions related to profiles

import json
from core.models import *
# store users records for transcript input
# assuming data format is as displayed in output; see sample transcript data
# assumes profile already exist; just adds in records from transcript
# MAY NEED: check if the user already has a record for that course?
def store_transcript(json_data):
	raw_data = json.loads(json_data)
	u = raw_data["user"]
	id = u["netid"]
	profile = Profile.objects.get(user__username=id)
	t = raw_data["transcript"]
	list_records = []
	for semester in t["courses"]:
		courses = t["courses"][semester]
		for c in courses:
			dept = c[:3]
			num = c[4:7]
			letter = ""
			if len(c) > 7:
				letter = c[7:8]
			try: # in case course isn't in database
				course = Course.objects.get(department=dept, number=num, letter=letter) 
				list_records.append(Record(course=course, semester=semester, profile=profile))
			except Course.DoesNotExist: # either actually not in database, or is a cross listing
				try:
					crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
					list_records.append(Record(course=crossed.course, semester=semester, profile=profile))
				except CrossListing.DoesNotExist:
					pass	

	Record.objects.bulk_create(list_records)

# store user records for manual input of courses
# REQUESTED sample input from manual form:
# ["PHY 104", "WRI 105", "FRS 118", "ECO 101A"]
# BASICALLY FINISHED
# NEED TO CHANGE HOW TO ACCESS PROFILE
# MAY NEED TO CHECK: IF COURSE IS ALREADY IN TRANSCRIPT AND USER WAS STUPID
def store_manual(raw_data):
	list_records = []
	for item in courses:
		dept = item[:3]
		num = item[4:7]
		letter = ""
		if len(item) > 7:
			letter = item[7:8]
		try: # in case course isn't in database
			course = Course.objects.get(department=dept, number=num, letter=letter) 
			list_records.append(Record(course=course, semester=semester, profile=profile))
		except Course.DoesNotExist: # either actually not in database, or is a cross listing
			try:
				crossed = CrossListing.objects.get(department=dept, number=num, letter=letter)
				list_records.append(Record(course=crossed.course, semester=semester, profile=profile))
			except CrossListing.DoesNotExist:
				# do something to tell us c was not added	
				pass

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

	Progress.objects.filter(calendar=calendar).delete() # delete old ones, start from scratch

	# degree requirements
	calculate_single_progress(calendar, calendar.degree)

	# requirements of major itself
	calculate_single_progress(calendar, calendar.major)

	# track requirements, if any
	track = calendar.track
	if track != NULL:
		calculate_single_progress(calendar, track)

	# certificates requirements, if any number
	for certificate in calendar.certificates:
		calculate_single_progress(calendar, certificate)

# calculate for one single degree/major/track/certificate; to be called from calculate_progress
# NEED TO DEBUG
def calculate_single_progress(calendar, category):
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
		number_choices.append(c) 
		other_than.append([])

		# create default progresses for all requirements, with number_taken = 0, completed = False
		list_progresses.append(Progress(calendar=calendar, requirement=requirement))
	Progress.objects.bulk_create(list_progresses)

	for record in Record.objects.filter(profile=calendar.profile).prefetch_related('course'):
		course = record.course
		matched = {}
		i = 0
		added = False
		for requirement in cat_requirements:
			if course in requirement.courses.all():
				matched[i] = requirement
				added = True

			nested_reqs = NestedReq.objects.filter(requirement=requirement).exclude(id__in=other_than[i])
			for nreq in nested_reqs:
				if course in nreq.courses.all() and added == False:
					matched[i] = [nreq, requirement]
					added = True
			i += 1
	
		if len(matched) == 0: # course did not satisfy any requirements; no Progresses need to be updated
			return

		elif len(matched) == 1: # course satisfied one requirement; need to update the progress
			index = 0
			req = None
			for key in matched: # there should only be one
				index = key
				if isinstance(matched[key], Requirement):
					req = matched[key]
				if isinstance(matched[key], list):
					nreq = matched[key][0]
					req = matched[key][1]
					other_than.append(nreq.id)
				progress = Progress.objects.get(calendar=calendar, requirement=req)	
				progress.number_taken += 1
				progress.courses_taken.add(course)
				number_remaining[index] -= 1

		else: # course satisfied multiple requirements
			diffs = []
			for j in range (0, len(number_choices)):
				diff.append(number_choices[j] - number_remaining[j] * FACTOR)

			min_key = 1000000
			for key in matched:
				if diff[key] < min_key:
					min_key = key

			if isinstance(matched[min_key], Requirement):
				req = matched[min_key]
			if isinstance(matched[min_key], list):
				nreq = matched[min_key][0]
				req = matched[min_key][1]
				other_than.append(nreq.id)			
			progress = Progress.objects.get(calendar=calendar, requirement=matched[min_key])
			progress.number_taken += 1
			progress.courses_taken.add(course)
			number_remaining[min_key] -= 1

# the brains of the project!!! 
# IN PROGRESS
def recommend(calendar):
	D = 13 # degree
	M = 12 # major
	T = 11 # track
	C = 10 # certificate
	WLD = 9 # white listed department
	WLA = 8 # white listed area
	BLD = 7 # black listed department
	BLA = 6 # black listed area
	F = 5 # flexibility; other BSE majors
	A = 4 # untaken distribution area

	profile = calendar.profile
	preference = Preference.objects.get(profile=profile)
	major = calendar.major
	other_majors = []
	for m in Major.objects.all():
		if m.name != major.name:
			other_majors.append(m)

	filter_out = []
	taken_areas = []
	# filter out courses they've taken already
	for record in Record.objects.get(profile=profile):
		filter_out.append(record.course)
		taken_areas.append(record.course.area)

	taken_areas.append("")
	# filter out black listed courses, no repeats
	for course in preference.bl_courses.all():
		if course not in filter_out:
			filter_out.append(course)

	# filter out courses already in calendar, no repeatss
	for semester in Semester.objects.filter(calendar=calendar):
		for course in semester.courses.all():
			if course not in filter_out:
				filter_out.append(course)

	wl_depts_short = [] # departments in wl_depts
	for dept in preference.wl_depts.all():
		wl_depts_short.append(dept.short_name)

	wl_areas = []
	for area in preference.wl_areas.all():
		wl_areas.append(area.short_name)

	bl_depts_short = []
	for dept in preference.bl_depts.all():
		bl_depts_short.append(dept.short_name)

	bl_areas = []
	for area in preference.bl_areas.all():
		bl_areas.append(area.short_name)

	bse_majors = []
	for major in Major.objects.all():
		majors.append(major.short_name)

	list_suggestions = []
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
		if course not in filter_out and course not in list_suggestions:
			department = course.department
			area = course.area

			entry = {'course_id': course.course_id, 'name': course.name, 'department': department,
			'number': course.number, 'letter': course.letter, 'short_name': department + " " + course.number + course.letter,
			'score': 0, 'reason': ""} 

			# add points if in wl_depts (primary department only)
			if department in wl_depts_short:
				entry['score'] += WLD

			# add points if in wl_areas
			if area in wl_areas:
				entry['score'] += WLA

			# subtract points if in bl_depts
			if department in bl_depts_short:
				entry['score'] -= BLD

			# subtract points if in bl_areas
			if area in bl_areas:
				entry['score'] += BLA

			# add points if satisfy untaken area
			if area not in taken_areas:
				entry['score'] += A

			# add points if satisfy degree requirements
			for req in calendar.degree.requirements.all():
				if course in req.courses.all():
					entry['score'] += D
					entry['reason'] += req.name + "requirement of your " + calendar.degree.short_name + " degree,\n"


			# add points if satisfy requirements of major itself
			for req in major.requirements.all():
				if course in req.courses.all():
					entry['score'] += M
					entry['reason'] += req.name + "requirement of your " + calendar.major.short_name + " major,\n" 

				nested_reqs = NestedReq.objects.filter(requirement=req)
				for nreq in nested_req:
					if course in nreq.courses.all():
						entry['score'] += M
						entry['reason'] += req.name + "requirement of your " + calendar.major.short_name + " major,\n" 					

			# add points if satisfy track
			for req in calendar.track.requirements.all():
				if course in req.courses.all():
					entry['score'] += M
					entry['reason'] += req.name + "requirement of your " + calendar.track.short_name + " track,\n" 

				nested_reqs = NestedReq.objects.filter(requirement=req)
				for nreq in nested_req:
					if course in nreq.courses.all():
						entry['score'] += M
						entry['reason'] += req.name + "requirement of your " + calendar.track.short_name + " track,\n" 		

			# for each certificate, add points if satisfy certificate
			for certificate in calendar.certificates.all():
				for req in certificate.requirements.all():
					if course in req.courses.all():
						entry['score'] += M
						entry['reason'] += req.name + "requirement of your " + certificate.short_name + " certificate,\n" 

					nested_reqs = NestedReq.objects.filter(requirement=req)
					for nreq in nested_req:
						if course in nreq.courses.all():
							entry['score'] += M
							entry['reason'] += req.name + "requirement of your " + certificate.short_name + " certificate,\n" 				

			# add points if satisfy flexibility (requirements of other majors themselves, excluding their tracks)
			for m in other_majors:
				for req in m.requirements.all():
					if course in req.courses.all():
						entry['score'] += M
						entry['reason'] += req.name + "requirement of the " + calendar.major.short_name + " major for flexibility,\n" 

					nested_reqs = NestedReq.objects.filter(requirement=req)
					for nreq in nested_req:
						if course in nreq.courses.all():
							entry['score'] += M
							entry['reason'] += req.name + "requirement of the " + calendar.major.short_name + " major for flexbility,\n" 					

			if len(reason) > 1:
				entry['reason'] = "This course satisfies the " + entry['reason']
				entry['reason'] = entry['reason'][:-2] # take off last ,\n
			list_suggestions.append(entry)

	sorted_list = sorted(list_suggestions, key=lambda k: k['score'])
	return sorted_list
