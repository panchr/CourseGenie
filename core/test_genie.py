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
# user1 = User.objects.create_user(username="user1")
# user1.save()
user1 = User.objects.get(username="user1")
prof1 = user1.profile

Record.objects.all().delete()
Calendar.objects.all().delete()
Progress.objects.all().delete()

c1 = Course.objects.get(department="PHY", number=104)
c2 = Course.objects.get(department="MAT", number=202)
c3 = Course.objects.get(department="COS", number=126)
rec1 = Record(profile=prof1, course=c1) # populates fake data about user
rec2 = Record(profile=prof1, course=c2)
rec3 = Record(profile=prof1, course=c3)
rec1.save()
rec2.save()
rec3.save()

degree1 = Degree.objects.get(short_name="B.S.E.")
major1 = Major.objects.get(short_name="MAE")
cal1 = Calendar(profile=prof1, degree=degree1 , major=major1)
cal1.save()
calculate_progress(cal1)
for progress in Progress.objects.all():
	print progress.requirement.name, progress

# tests recommend()
'''
results = recommend(cal1)
for i, item in enumerate(results, 1):
	print i
	for key, value in item.items():
		if isinstance(value, (str, unicode)):
			value = value.encode('utf-8')
		print key, value
'''