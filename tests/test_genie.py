# -*- coding: utf-8 -*-
# random test cases
import sys
import os
if os.path.dirname(os.getcwd()) == 'scripts':
	os.chdir('..')
	sys.path.append(os.path.abspath('..'))
else:
	sys.path.append(os.path.abspath('.'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursegenie.settings")
import django
django.setup()
from django.contrib.auth.models import User

from core.models import *
from core.genie import calculate_progress, recommend

# tests calculate_progress and calculate_single_progress
'''
user1, _ = User.objects.get_or_create(username='user1')
prof1 = user1.profile
'''
user1, _ = User.objects.get_or_create(username='zyfan')
prof1 = user1.profile
# CASE ONE
'''
c1 = Course.objects.get(department="PHY", number=104)
c2 = Course.objects.get(department="MAT", number=202)
c3 = Course.objects.get(department="COS", number=126)
rec1, _ = Record.objects.get_or_create(profile=prof1, course=c1)
rec2, _ = Record.objects.get_or_create(profile=prof1, course=c2)
rec3, _ = Record.objects.get_or_create(profile=prof1, course=c3)
'''

# CASE TWO
'''
rec_ids = []
c1 = Course.objects.get(department="PHY", number=104)
c2 = Course.objects.get(department="MAT", number=202)
c3 = Course.objects.get(department="COS", number=126)
c4 = Course.objects.get(department="PHY", number=103)
c5 = Course.objects.get(department="MAT", number=201)
c6 = Course.objects.get(department="FRE", number=207)
c7 = Course.objects.get(department="COS", number=333)
c8 = Course.objects.get(department="ORF", number=309)
c9 = Course.objects.get(department="COS", number=461)
c10 = Course.objects.get(department="COS", number=340)
rec1, _ = Record.objects.get_or_create(profile=prof1, course=c1)
rec2, _ = Record.objects.get_or_create(profile=prof1, course=c2)
rec3, _ = Record.objects.get_or_create(profile=prof1, course=c3)
rec4, _ = Record.objects.get_or_create(profile=prof1, course=c4)
rec5, _ = Record.objects.get_or_create(profile=prof1, course=c5)
rec6, _ = Record.objects.get_or_create(profile=prof1, course=c6)
rec7, _ = Record.objects.get_or_create(profile=prof1, course=c7)
rec8, _ = Record.objects.get_or_create(profile=prof1, course=c8)
rec9, _ = Record.objects.get_or_create(profile=prof1, course=c9)
rec10, _ = Record.objects.get_or_create(profile=prof1, course=c10)
'''

degree1 = Degree.objects.get(short_name="B.S.E.")
major1 = Major.objects.get(short_name="COS")
cal1, _ = Calendar.objects.get_or_create(profile=prof1, degree=degree1 , major=major1)
calculate_progress(cal1)
for progress in Progress.objects.all():
 	print progress

# tests recommend()
results = recommend(cal1)

for i, item in enumerate(results, 1):
	print i
	for key, value in item.items():
		if isinstance(value, (str, unicode)):
			value = value.encode('utf-8')
		if key == 'score' or key == 'reason':
			print key, value
		if key == 'course':
			print value.department + str(value.number)