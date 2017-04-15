from core.models import Degree, Major, Certificate, Track, Course, CrossListing, Requirement, NestedReq, Profile, Record, Calendar, Progress, Area, Department, Preference, Semester
from django.contrib.auth.models import User
from rest_framework import serializers

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('name', 'short_name')
        
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('short_name')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

class NestedReqSerializer(serializers.ModelSerializer):
    class Meta:
        model = NestedReq
        fields = ('number', 'courses', 'requirement')

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('profile', 'course', 'grade', 'semester')

class CrossListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrossListing
        fields = ('course', 'number', 'letter', 'department')

class CourseSerializer(serializers.ModelSerializer):
    listings = CrossListingSerializer(read_only=True)
    records = RecordSerializer(source='record_set')

    class Meta:
        model = Course
        fields = ('name', 'course_id', 'number', 'letter', 'department', 'area', 'term', 'listings', 'records')

class PreferenceSerializer(serializers.ModelSerializer):
    bl_courses = CourseSerializer(many = True, read_only=True)
    bl_areas = AreaSerializer(many = True, read_only=True)
    bl_depts = DepartmentSerializer(many = True, read_only=True)
    wl_areas = AreaSerializer(many = True, read_only=True)
    wl_depts = DepartmentSerializer(many = True, read_only=True)

    class Meta:
        model = Preference
        fields = ('profile', 'bl_courses', 'bl_areas', 'bl_depts', 'wl_areas', 'wl_depts')

class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many = True, read_only=True)

    class Meta:
        model = Semester
        fields = ('name', 'calendar', 'courses')

class ProgressSerializer(serializers.ModelSerializer):
    courses_taken = CourseSerializer(many = True, read_only=True)

    class Meta:
        model = Progress
        fields = ('calendar', 'courses_taken', 'number_taken', 'completed', 'requirement')

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ('name', 'short_name', 'requirements')

class CalendarSerializer(serializers.ModelSerializer):
    certificates = CertificateSerializer(many = True, read_only=True)
    sandbox = CourseSerializer(many = True, read_only=True)
    progress = ProgressSerializer(read_only=True)
    semesters = SemesterSerializer(read_only=True)

    class Meta:
        model = Calendar
        fields = ('profile', 'major', 'certificates', 'sandbox', 'last_accessed', 'progress', 'semesters')

class TrackSerializer(serializers.ModelSerializer):
    calendars = CalendarSerializer(read_only=True)

    class Meta:
        model = Track
        fields = ('major', 'name', 'short_name', 'requirements', 'calendars')

class MajorSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(read_only=True)
    calendars = CalendarSerializer(read_only=True)

    class Meta:
        model = Major
        fields = ('name', 'short_name', 'degree', 'requirements', 'tracks', 'calendars')

class DegreeSerializer(serializers.ModelSerializer):
    majors = MajorSerializer(read_only=True)
    calendars = CalendarSerializer(read_only=True)

    class Meta:
        model = Degree
        fields = ('name', 'short_name', 'requirements', 'majors', 'calendars')

class RequirementSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many = True, read_only=True)
    nested_reqs = NestedReqSerializer(read_only=True)
    progress = ProgressSerializer(read_only=True)

    class Meta:
        model = Requirement
        fields = ('name', 't', 'number', 'notes', 'courses', 'content_type', 'object_id', 'parent', 'nested_reqs', 'progress', 'degree', 'major', 'certificate', 'track')

    def to_representation(self, value):
        if isinstance(value, Degree):
            serializer = DegreeSerializer(value)
        elif isinstance(value, Major):
            serializer = MajorSerializer(value)
        elif isinstance(value, Certificate):
            serializer = CertificateSerializer(value)
        elif isinstance(value, Track):
            serializer = TrackSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    records = RecordSerializer(read_only=True)
    preferences = PreferenceSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ('user', 'year', 'records', 'preferences')