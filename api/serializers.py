from core.models import Degree, Major, Certificate, Track, Course, CrossListing, Requirement, NestedReq, Profile, Record, Calendar, Progress, Area, Department, Preference, Semester
from django.contrib.auth.models import User
from rest_framework import serializers

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'is_superuser', 'is_staff',
            'is_active', 'date_joined', 'groups', 'user_permissions')

class NestedReqSerializer(serializers.ModelSerializer):
    class Meta:
        model = NestedReq
        fields = '__all__'

class CrossListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrossListing
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    listings = CrossListingSerializer(many=True, read_only=True)
    term_display = serializers.CharField(source='get_term_display')
    short_name = serializers.CharField(source='__str__')

    class Meta:
        model = Course
        fields = '__all__'

class RecordSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Record
        fields = '__all__'

class PreferenceSerializer(serializers.ModelSerializer):
    bl_courses = CourseSerializer(many = True, read_only=True)
    bl_areas = AreaSerializer(many = True, read_only=True)
    bl_depts = DepartmentSerializer(many = True, read_only=True)
    wl_areas = AreaSerializer(many = True, read_only=True)
    wl_depts = DepartmentSerializer(many = True, read_only=True)

    class Meta:
        model = Preference
        fields = '__all__'

class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many = True, read_only=True)
    term_display = serializers.CharField(source='get_term_display')

    class Meta:
        model = Semester
        fields = '__all__'

class ProgressSerializer(serializers.ModelSerializer):
    courses_taken = CourseSerializer(many=True, read_only=True)
    #calendar = CalendarSerializer(read_only=True)

    class Meta:
        model = Progress
        fields = '__all__'

class RequirementSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many = True, read_only=True)
    nested_reqs = NestedReqSerializer(many=True, read_only=True)

    class Meta:
        model = Requirement
        fields = '__all__'

    # def to_representation(self, value):
    #     if isinstance(value, Degree):
    #         serializer = DegreeSerializer(value)
    #     elif isinstance(value, Major):
    #         serializer = MajorSerializer(value)
    #     elif isinstance(value, Certificate):
    #         serializer = CertificateSerializer(value)
    #     elif isinstance(value, Track):
    #         serializer = TrackSerializer(value)
    #     else:
    #         raise Exception('Unexpected type of tagged object: %s' % type(value))

    #     return serializer.data

class CertificateSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Certificate
        fields = '__all__'

class DegreeSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Degree
        fields = '__all__'

class MajorSerializer(serializers.ModelSerializer):
    degree = DegreeSerializer(read_only=True)
    requirements = RequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Major
        fields = '__all__'

class TrackSerializer(serializers.ModelSerializer):
    major = MajorSerializer(read_only=True)
    requirements = RequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    records = RecordSerializer(many=True, read_only=True)
    preferences = PreferenceSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

class CalendarSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    # degree = DegreeSerializer(read_only=True)
    # major = MajorSerializer(read_only=True)
    # track = TrackSerializer(read_only=True)
    # certificates = CertificateSerializer(many=True, read_only=True)
    sandbox = CourseSerializer(many=True, read_only=True)
    semesters = SemesterSerializer(many=True, read_only=True)

    class Meta:
        model = Calendar
        fields = '__all__'

class RecommendationSerializer(serializers.Serializer):
    course = CourseSerializer()
    reason = serializers.CharField()
    score = serializers.IntegerField()
    reason_list = serializers.ListField(
        child=serializers.CharField())
