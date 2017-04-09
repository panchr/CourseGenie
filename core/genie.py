# core/genie.py
# CourseGenie
# Author: Kathy Fan
# Date: April 5th, 2017
# functions related to profiles

import json

# store user’s records for transcript input
# assuming data format is as displayed in output; see sample transcript data. NEED TO CONFIRM
# assumes profile already exist; just adds in records from transcript
# NEED TO CHANGE FORMAT
# NEED TO CHANGE HOW TO ACCESS PROFILE
# MAY NEED TO CHECK: IF COURSE WAS FILLED MANUALLY BY CONFUSED USER
def store_transcript(profile, json_data):
	raw_data = json.loads(json_data)
	u = raw_data["user"]
	id = u["netid"]
	profile = Profile.objects.get(user__username=id)
	t = raw_data["transcript"]
	list_records = []
	for semester in t["courses"]:
		courses = t["courses"][semester]
		for c in courses: # need to actually get the Course object
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
					# do something to tell us c was not added	
					pass	

	Record.objects.bulk_create(list_records)

# store user’s records for manual input of courses
# REQUESTED sample input from manual form:
# ["PHY 104", "WRI 105", "FRS 118", "ECO 101A"]
# BASICALLY FINISHED
# NEED TO CHANGE HOW TO ACCESS PROFILE
# MAY NEED TO CHECK: IF COURSE IS ALREADY IN TRANSCRIPT AND USER WAS STUPID
def store_manual(raw_data):
	list_records = []
	for item in courses: # need to actually get the Course object
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

# calculate progress corresponding to a calendar
# key idea: a course should not be able to satisfy multiple requirements under the same category
# NEED TO DEBUG
def calculate_progress(calendar):
	profile = calendar.profile

	Progress.objects.filter(calendar=calendar).delete() # delete old ones, start from scratch

	# degree requirements (simpler scenario than other progresses)
	degree = calendar.degree
	for requirement in  degree.requirements.all():
		progress = Progress(calendar=calendar, requirement=requirement)
			progress.save()

		number_taken = 0
		for course in requirement.courses.all():
			try:
				record = Record.objects.get(profile=profile, course=course) # took this course
				number_taken += 1
				progress.courses.add(course)
			except Record.DoesNotExist: # did not take the course
				pass

		if number_taken >= requirement.number:		
			progress.completed = True

		progress.number_taken = number_taken

	# requirements of major itself
	calculate_single_progress(calendar, calendar.major)

	# track requirements, if any
	track = calendar.track
	if track != NULL:
		calculate_single_progress(calendar, track)

	# certificates requirements, if any number
	for certificate in calendar.certificates:
		calculate_single_progress(calendar, certificate)

# calculate for one single major/track/certificate; to be called from calculate_progress
# NEED TO DEBUG
def calculate_single_progress(calendar, category):
	FACTOR = 5
	number_choices = [] # number of courses to choose from for this requirement
	number_remaining = [] # number of courses left to fulfill for this requirement
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
		# create default progresses for all requirements, with number_taken = 0, completed = False
		list_progresses.append(Progress(calendar=calendar, requirement=requirement))
	Progress.objects.bulk_create(list_progresses)

	for record in Record.objects.filter(profile=calendar.profile).prefetch_related('course'):
		course = record.course
		matched_reqs = {}
		i = 0
		added = False
		for requirement in cat_requirements:
			if course in requirement.courses:
				matched_reqs[i] = requirement
				added = True

			nested_reqs = requirement.nested_reqs.all()
			for nreq in nested_reqs:
				if course in nreq.courses and added == False:
					matched_reqs[i] = requirement
					added = True
			i += 1
	
		if len(matched_reqs) == 0: # course did not satisfy any requirements; no Progresses need to be updated
			return

		elif len(matched_reqs) == 1: # course satisfied one requirement; need to update the progress
			index = 0
			req = None
			for key in matched_reqs: # there should only be one
				index = key
				req = matched_reqs[key]

			progress = Progress.objects.get(calendar=calendar, requirement=req)	

			progress.number_taken += 1
			progress.courses_taken.add(course)
			number_remaining[index] -= 1

		else: # course satisfied multiple requirements
			diffs = []
			for j in range (0, len(number_choices)):
				diff.append(number_choices[j] - number_remaining[j] * FACTOR)

			min_key = 1000000
			for key in matched_reqs:
				if diff[key] < min_key:
					min_key = key

			progress = Progress.objects.get(calendar=calendar, requirement=matched_reqs[min_key])

			progress.number_taken += 1
			progress.courses_taken.add(course)
			number_remaining[min_key] -= 1

# recommend courses from student’s past courses, degree requirements, 
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
