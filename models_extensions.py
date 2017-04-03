# to be added to core/models.py
# Author: Kathy Fan
# Date: April 1st, 2017
# models for user information

# weird indenting ... seems to be a hard tabs/soft tabs issue
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
    
    def __str__(self):
        return self.user.username

# automatically create profile when create user
# according to https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: 
        Profile.objects.create(user=instance, year=0)

# not completed
#class Satisfied_reqs(models.Model):
#	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='satisfied_reqs')

class Record(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='record')
    course = models.ForeignKey(Course)
    grade = models.CharField(max_length = 3)
    semester = models.CharField(max_length = 25)
    
    def __str__(self):
    	return '{} {} {}'.format(self.semester, self.course, self.grade)

class Calendar(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='calendar')
    major = models.ForeignKey(Major)
    certificates = GenericRelation('Certificate', related_query_name = 'calendar')
    sandbox = GenericRelation('Course', related_query_name = 'sandbox')
    
    def all_semesters(self):
    '''Retrieve all semesters for the calendar.'''
    return Record.objects.filter(
        models.Q(calendar = self))

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
	name = models.CharField(max_length = 25)
	calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='semester')
    courses = models.ManyToManyField(Course)

    def __str__(self):
    	return self.name

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