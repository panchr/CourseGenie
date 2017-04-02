# to be added to core/models.py
# Author: Kathy Fan
# Date: April 1st, 2017
# models for user information

from django.contrib.auth.models import User

class Profile(models.Model):
    ''' 
    afaik User has various fields already, so for example, we can set the username = netid,
    and make use of the first_name, last_name, email, etc fields. But does using the User
    model work/make sense if we're doing a CAS authentication instead of Django's own 
    authentication?
    '''
    user = models.OneToOneField(User, on_delete = models.CASCADE) # Django User model
    year = models.IntegerField(max_length = 4) # graduation year
    calendars = GenericRelation('Calendar', related_query_name = 'profile')
    records = GenericRelation('Record', related_query_name = 'profile') # courses taken
    
    def all_records(self):
        '''Retrieve all records for the profile.'''
        return Record.objects.filter(
            models.Q(profile = self))
    
    def all_calendars(self):
        '''Retrieve all calendars for the profile.'''
        return Calendar.objects.filter(
            models.Q(profile = self))
    
    def __str__(self):
        return self.user.username

# automatically create/update profile when create/update user
# according to https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: 
        Profile.objects.create(user = instance)

@receiver(post_save, sender = User)
def save_user_profile(sender, instance, **kwargs)
    instance.profile.save()

class Record(models.Model): # need an on_delete = ?
    course = models.ForeignKey(Course)
    grade = models.CharField(max_length = 3)
    semester = models.CharField(max_length = 25)
    
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('content_type', 'object_id')
    
    def __str__(self):
    	return '{} {} {}'.format(self.semester, self.course, self.grade)

class Calendar(models.Model): # need an on_delete = ?
    major = models.ForeignKey(Major)
    certificates = GenericRelation('Certificate', related_query_name = 'calendar')
    sandbox = GenericRelation('Course', related_query_name = 'sandbox')
    semesters = GenericRelation('Semester', related_query_name='Calendar')
    
    def all_semesters(self):
    '''Retrieve all semesters for the calendar.'''
    return Record.objects.filter(
        models.Q(calendar = self))
    
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
    	return '{} {} {}'.format(self.major, self.certificates) # not sure if this works
    	
# preference is a property of a user's profile and consistent across calendars
class Preference(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,
        related_name='preferences')
    # bl: black listed
    bl_courses = models.ManyToManyField(Course)
    bl_area = models.ManyToManyField(Area)
    bl_dept = models.ManyToManyField(Department)
    
    # wl: white listed
    wl_area = models.ManyToManyField(Area)
    wl_dept = models.ManyToManyField(Department)
    
    def __str__(self):
    	return "preference"

class Semester(models.Model):
    courses = models.ManyToManyField(Course)

    def __str__(self):
    	return self.courses # not sure if this works

class Area(models.Model): # distribution area
    name = models.CharField(max_length = 50)
    short_name = models.CharField(max_length = 3)
    
    def __str__(self):
    	return self.short_name

class Department(models.Model):
    name = models.CharField(max_length = 50)
    short_name = models.CharField(max_length = 3)

    def __str__(self):
    	return self.name