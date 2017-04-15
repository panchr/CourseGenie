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
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator


class Degree(models.Model):
	name = models.CharField(max_length=255, unique=True)
	short_name = models.CharField(max_length=15, unique=True)
	requirements = GenericRelation('Requirement', related_query_name='degree')

	def __str__(self):
		return self.short_name

class Major(models.Model):
	name = models.CharField(max_length=255, unique=True)
	short_name = models.CharField(max_length=15, unique=True)
	degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='majors')
	requirements = GenericRelation('Requirement', related_query_name='major')

	def all_requirements(self):
		'''Retrieve all requirements for the major.'''
		return Requirements.objects.filter(
			models.Q(major=self) | models.Q(degree=self.degree_id))

	def __str__(self):
		return self.short_name

	class Meta:
		unique_together = ('name', 'degree')

class Certificate(models.Model):
	name = models.CharField(max_length=255, unique=True)
	short_name = models.CharField(max_length=50, unique=True)
	requirements = GenericRelation('Requirement',
		related_query_name='certificate')

	def all_requirements(self):
		'''Retrieve all requirements for the major.'''
		return Requirements.objects.filter(
			models.Q(certificate=self) | models.Q(degree=self.degree_id))
			
	def __str__(self):
		return self.short_name

class Track(models.Model):
	major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='tracks')
	name = models.CharField(max_length=255)
	short_name = models.CharField(max_length=15)
	requirements = GenericRelation('Requirement', related_query_name='track')

	def all_requirements(self):
		'''Retrieve all requirements for the certificate.'''
		return Requirements.objects.filter(
			models.Q(track=self) | models.Q(degree=self.degree_id))

	def __str__(self):
		return self.short_name

	class Meta:
		unique_together = ('major', 'name')

class Course(models.Model):
	name = models.CharField(max_length=255)
	course_id = models.CharField(max_length=10, default="", unique=True)
	number = models.PositiveSmallIntegerField()
	letter = models.CharField(max_length=1, default="")
	department = models.CharField(max_length=3)
	area = models.CharField(max_length=3, default="")

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
		return '{} {}{}'.format(self.department, self.number, self.letter)

	class Meta:
		unique_together = ('number', 'department', 'letter')

class CrossListing(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE,
		related_name='listings')
	number = models.PositiveSmallIntegerField()
	letter = models.CharField(max_length=1, default="")
	department = models.CharField(max_length=3)

	def __str__(self):
		return '{} {} {}'.format(self.department, self.number, self.letter)
		#return '{} {}'.format(self.department, self.number)
	class Meta:
		unique_together = ('course', 'number', 'department', 'letter')
	
class Requirement(models.Model):
	name = models.CharField(max_length=255)
	t = models.CharField(max_length=50) # requirement type
	number = models.PositiveSmallIntegerField(default=0) # number required
	notes = models.CharField(max_length=255, default='')
	intrinsic_score = models.PositiveSmallIntegerField(default=0)

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
		unique_together = ('content_type', 'object_id', 't')

# belongs under a requirement
class NestedReq(models.Model):
	number = models.PositiveSmallIntegerField()
	courses = models.ManyToManyField(Course)
	requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='nested_reqs')

	def __str__(self):
		return self.number

class Profile(models.Model):
		user = models.OneToOneField(User, on_delete = models.CASCADE, unique=True) # Django User model
		year = models.PositiveSmallIntegerField(validators=[MinValueValidator(2015)]) # graduation year
		submitted = models.BooleanField(default=False)
		
		def __str__(self):
				return self.user.username

		def course_list(self):
			return map(str, self.records.all())

# automatically create profile when create user
# according to https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):
		if created:
			Profile.objects.create(user=instance, year=0)

class Record(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='records')
	course = models.ForeignKey(Course)
	semester = models.CharField(max_length = 25, default="")
	
	def __str__(self):
		return self.course.name

class Calendar(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='calendars')
	degree = models.ForeignKey(Degree)
	major = models.ForeignKey(Major)
	track = models.ForeignKey(Track, blank=True, null=True) # optional 
	certificates = models.ManyToManyField(Certificate)
	sandbox = models.ManyToManyField(Course)
	last_accessed = models.DateTimeField(auto_now=True)

	class Meta: # most recently accessed is returned first
		ordering = ['-last_accessed']
	
	def __str__(self):
		return '{} {}'.format(self.major, self.track)
 
# a calendar has progresses corresponding to all requirements
class Progress(models.Model):
	calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='progress')
	courses_taken = models.ManyToManyField(Course)
	number_taken = models.PositiveSmallIntegerField(default=0)
	completed = models.BooleanField(default=False)
	requirement = models.ForeignKey(Requirement, related_name='progress')

	class Meta:
		unique_together = ('calendar', 'requirement')

	def __str__(self):
		return '{} {} {}'.format(self.requirement.name, self.number_taken, self.completed)

class Area(models.Model): # distribution area
	#name = models.CharField(max_length = 50)
	short_name = models.CharField(max_length = 3, unique=True)
		
	def __str__(self):
		return self.short_name

class Department(models.Model):
	name = models.CharField(max_length = 50, unique=True)
	short_name = models.CharField(max_length = 3, unique=True)

	def __str__(self):
		return self.short_name
					
# preference is a property of a user's profile and consistent across calendars
class Preference(models.Model):
	# change to 1-to-1 relationship
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE,
				related_name='preferences')
		# bl: black listed. NOTE: not sure if these related_names work
	bl_courses = models.ManyToManyField(Course)
	bl_areas = models.ManyToManyField(Area, related_name='bl_area')
	bl_depts = models.ManyToManyField(Department, related_name='bl_dept')
		
		# wl: white listed
	wl_areas = models.ManyToManyField(Area, related_name='wl_course')
	wl_depts = models.ManyToManyField(Department, related_name='wl_dept')

	def __str__(self):
		return "preference"

class Semester(models.Model):
	name = models.CharField(max_length=25)
	calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='semester')
	courses = models.ManyToManyField(Course)

	class Meta:
		unique_together = ('name', 'calendar')

	def __str__(self):
		return self.name
