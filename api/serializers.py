from core.models import Degree, Major, Certificate, Track, Course, CrossListing, Requirement, Profile, Record, Calendar, Progress, Area, Department, Preference, Semester
from rest_framework import serializers

class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ('name', 'short_name', 'requirements')


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ('name', 'short_name', 'degree', 'requirements')

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ('name', 'short_name', 'requirements')

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('major', 'name', 'short_name', 'requirements')

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('name', 'course_id', 'number', 'letter', 'department', 'area', 'term')

class CrossListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrossListing
        fields = ('course', 'number', 'letter', 'department')

class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = ('name', 't', 'number', 'notes', 'courses', 'content_type', 'object_id', 'parent')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'year')

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('profile', 'course', 'grade', 'semester')

class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ('profile', 'major', 'certificates', 'sandbox', 'last_accessed')

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ('calendar', 'courses_taken', 'number_taken', 'completed', 'requirement')

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('short_name')

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('name', 'short_name')

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ('profile', 'bl_courses', 'bl_areas', 'bl_depts', 'wl_areas', 'wl_depts')

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ('name', 'calendar', 'courses')