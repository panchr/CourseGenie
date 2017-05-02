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

class BasicRequirementSerializer(serializers.ModelSerializer):
    parent_t = serializers.CharField(source='content_type.model')

    class Meta:
        model = Requirement
        # fields = '__all__'
        exclude = ('courses',)

class RequirementSerializer(BasicRequirementSerializer):
    courses = CourseSerializer(many = True, read_only=True)
    nested_reqs = NestedReqSerializer(many=True, read_only=True)

class BasicCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'

class CertificateSerializer(BasicCertificateSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)

class BasicDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = '__all__'

class DegreeSerializer(BasicDegreeSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)

class BasicMajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = '__all__'

class MajorSerializer(BasicMajorSerializer):
    degree = DegreeSerializer(read_only=True)
    requirements = RequirementSerializer(many=True, read_only=True)

class BasicTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'

class TrackSerializer(BasicTrackSerializer):
    major = MajorSerializer(read_only=True)
    requirements = RequirementSerializer(many=True, read_only=True)

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
    certificates = BasicCertificateSerializer(many=True, read_only=True)
    sandbox = CourseSerializer(many=True, read_only=True)
    semesters = SemesterSerializer(many=True, read_only=True)

    class Meta:
        model = Calendar
        fields = '__all__'

class ProgressSerializer(serializers.ModelSerializer):
    # courses_taken = CourseSerializer(many=True, read_only=True)
    # calendar = CalendarSerializer(read_only=True)
    requirement = BasicRequirementSerializer(read_only=True)
    parent = serializers.SerializerMethodField()

    def get_parent(self, obj):
        parent = obj.requirement.parent
        if isinstance(parent, Degree):
            return BasicDegreeSerializer(parent).data
        elif isinstance(parent, Major):
            return BasicMajorSerializer(parent).data
        elif isinstance(parent, Track):
            return BasicTrackSerializer(parent).data
        elif isinstance(parent, Certificate):
            return BasicCertificateSerializer(parent).data
        else:
            return None

    class Meta:
        model = Progress
        fields = '__all__'

class RecommendationSerializer(serializers.Serializer):
    course = CourseSerializer()
    reason = serializers.CharField()
    score = serializers.IntegerField()
    reason_list = serializers.ListField(
        child=serializers.CharField())
