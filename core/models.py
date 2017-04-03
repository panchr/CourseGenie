# core/models.py
# CourseGenie
# Author: Rushy Panchal
# Date: March 24th, 2017
# Description: Core database models.

from django.db import models
from django.contrib.contenttypes.fields import (
	GenericForeignKey,
	GenericRelation
	)
from django.contrib.contenttypes.models import ContentType

class Degree(models.Model):
	name = models.CharField(max_length=255)
	short_name = models.CharField(max_length=15)
	requirements = GenericRelation('Requirement', related_query_name='degree')

	def __str__(self):
		return self.short_name

class Major(models.Model):
	name = models.CharField(max_length=255)
	short_name = models.CharField(max_length=15)
	degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
	requirements = GenericRelation('Requirement', related_query_name='major')

	def all_requirements(self):
		'''Retrieve all requirements for the major.'''
		return Requirements.objects.filter(
			models.Q(major=self) | models.Q(degree=self.degree_id))

	def __str__(self):
		return self.short_name

class Certificate(models.Model):
	name = models.CharField(max_length=255)
	short_name = models.CharField(max_length=15)
	requirements = GenericRelation('Requirement',
		related_query_name='certificate')

	def all_requirements(self):
		'''Retrieve all requirements for the major.'''
		return Requirements.objects.filter(
			models.Q(certificate=self) | models.Q(degree=self.degree_id))
			
	def __str__(self):
		return self.short_name

class Track(models.Model):
	major = models.ForeignKey(Major, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	short_name = models.CharField(max_length=15)
	requirements = GenericRelation('Requirement', related_query_name='track')

	def all_requirements(self):
		'''Retrieve all requirements for the certificate.'''
		return Requirements.objects.filter(
			models.Q(track=self) | models.Q(degree=self.degree_id))

	def __str__(self):
		return self.short_name

class Course(models.Model):
	name = models.CharField(max_length=255)
	number = models.CharField(max_length=3)
	#letter = models.CharField(max_length=1, default="")
	department = models.CharField(max_length=3)
	area = models.CharField(max_length=3)

	TERM_FALL = 1
	TERM_SPRING = 2
	TERM_BOTH = 3
	TERM_INCONSISTENT = 4 # Inconsistent offerings
	term = models.PositiveSmallIntegerField(choices=(
		(TERM_FALL, 'Fall'),
		(TERM_SPRING, 'Spring'),
		(TERM_BOTH, 'Fall & Spring'),
		(TERM_INCONSISTENT, 'Inconsistent'),
		), default=TERM_INCONSISTENT)

	def __str__(self):
		#return '{} {} {}'.format(self.department, self.number, self.letter)
		return '{} {}'.format(self.department, self.number)
	class Meta:
		unique_together = ('number', 'department')

class CrossListing(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE,
		related_name='listings')
	number = models.CharField(max_length=4)
	letter = models.CharField(max_length=1, default="")
	department = models.CharField(max_length=3)

	def __str__(self):
		#return '{} {} {}'.format(self.department, self.number, self.letter)
		return '{} {}'.format(self.department, self.number)
	class Meta:
		unique_together = ('course', 'number', 'department')
	
class Requirement(models.Model):
	name = models.CharField(max_length=255)
	t = models.CharField(max_length=50) # requirement type
	number = models.PositiveIntegerField(default=0) # number required
	notes = models.CharField(max_length=255, default='')

	# Courses can be listed in many different requirements
	courses = models.ManyToManyField(Course)

	# Requirements can be listed under either Majors, Degrees, Certificates, or
	# Tracks.
	# See:
	# 	- https://docs.djangoproject.com/en/1.10/ref/contrib/contenttypes/#generic-relations
	# 	- https://stackoverflow.com/a/6336509/1730261
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
		limit_choices_to=(
			models.Q(app_label='core', model='Major')
			| models.Q(app_label='core', model='Degree')
			| models.Q(app_label='core', model='Certificate')
			| models.Q(app_label='core', model='Track')
			))
	object_id = models.PositiveIntegerField()
	parent = GenericForeignKey('content_type', 'object_id')

	def __str__(self):
		return '{}: {} ({})'.format(self.parent, self.t, self.number)

	class Meta:
		unique_together = ('object_id', 't')
