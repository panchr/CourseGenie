import re

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import NotFound, NotAcceptable
from rest_framework.response import Response

from api.serializers import *
from core.models import *
from core.errors import *
from core import genie

# things that should not be changed
class DegreeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Degree.objects.all()
    serializer_class = DegreeSerializer

class MajorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer

class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CrossListingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CrossListing.objects.all()
    serializer_class = CrossListingSerializer

class RequirementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer

class NestedReqViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NestedReq.objects.all()
    serializer_class = NestedReqSerializer

# things that can be changed
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class CalendarViewSet(viewsets.ModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer

class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

class PreferenceViewSet(viewsets.ModelViewSet):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer

    @detail_route(methods=['post', 'delete'], url_path='bl-course')
    def modify_course(self, request, pk=None):
        pref = self.get_object()
        search_kwargs = {}
        if 'course_id' in request.query_params:
            search_kwargs['course_id'] = request.query_params['course_id']
        else:
            course_re = re.compile(r'^(?P<dept>[A-Z]{3}) (?P<num>\d{3})(?P<letter>[A-Z]?)$')
            short_name = course_re.match(request.query_params['short_name'])
            if not short_name:
                raise NotAcceptable(detail='unacceptable')

            search_kwargs['number'] = short_name.group('num')
            search_kwargs['department'] = short_name.group('dept')
            if short_name.group('letter'):
                search_kwargs['letter'] = short_name.group('letter')

        try:
            course = Course.objects.get(**search_kwargs)
        except Course.DoesNotExist:
            raise NotFound('course %s not found' % course_id)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if pref.bl_courses.filter(id=course.id).exists():
                raise ContentError('course %s already in blacklist' % course_id)

            pref.bl_courses.add(course)
        elif request.method == 'DELETE':
            if not pref.bl_courses.filter(id=course.id).exists():
                raise ContentError('course %s not in blacklist' % course_id)

            pref.bl_courses.remove(course)

        return Response({'success': True})

    @detail_route(methods=['post', 'delete'], url_path='area')
    def modify_area(self, request, pk=None):
        pref = self.get_object()
        short_name = request.query_params['short_name']
        t = request.query_params['t']

        if t not in {'wl', 'bl'}:
            raise NotFound('area %s not found for type %s' % (short_name, t))

        if t == 'wl':
            pref_list = pref.wl_areas
            other_list = pref.bl_areas
        else:
            pref_list = pref.bl_areas
            other_list = pref.wl_areas

        try:
            area = Area.objects.get(short_name=short_name)
        except Area.DoesNotExist:
            raise NotFound('area %s not found' % short_name)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if pref_list.filter(id=area.id).exists():
                raise ContentError('area %s already in list' % short_name)

            if other_list.filter(id=area.id).exists():
                raise ContentError('area %s in opposing list' % short_name)

            pref_list.add(area)
        elif request.method == 'DELETE':
            if not pref_list.filter(id=area.id).exists():
                raise ContentError('area %s not in list' % short_name)

            pref_list.remove(area)

        return Response({'success': True})

    @detail_route(methods=['post', 'delete'], url_path='dept')
    def modify_dept(self, request, pk=None):
        pref = self.get_object()
        short_name = request.query_params['short_name']
        t = request.query_params['t']

        if t not in {'wl', 'bl'}:
            raise NotFound('dept %s not found for type %s' % (short_name, t))

        if t == 'wl':
            pref_list = pref.wl_depts
            other_list = pref.bl_depts
        else:
            pref_list = pref.bl_depts
            other_list = pref.wl_depts

        try:
            dept = Department.objects.get(short_name=short_name)
        except Department.DoesNotExist:
            raise NotFound('dept %s not found' % short_name)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if pref_list.filter(id=dept.id).exists():
                raise ContentError('dept %s already in list' % short_name)

            if other_list.filter(id=dept.id).exists():
                raise ContentError('dept %s in opposing list' % short_name)

            pref_list.add(dept)
        elif request.method == 'DELETE':
            if not pref_list.filter(id=dept.id).exists():
                raise ContentError('dept %s not in list' % short_name)

            pref_list.remove(dept)

        return Response({'success': True})

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

    @detail_route(methods=['post', 'delete'], url_path='course')
    def modify_course(self, request, pk=None):
        semester = self.get_object()
        course_id = request.query_params['course_id']
        try:
            course = Course.objects.get(course_id=course_id)
        except Course.DoesNotExist:
            raise NotFound('course %s not found' % course_id)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if semester.courses.filter(id=course.id).exists():
                raise ContentError('course %s already in semester' % course_id)

            semester.courses.add(course)
        elif request.method == 'DELETE':
            if not semester.courses.filter(id=course.id).exists():
                raise ContentError('course %s not in semester' % course_id)

            semester.courses.remove(course)

        return Response({'success': True})

class ProgressViewSet(viewsets.ModelViewSet):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer

# calculated on the stop
class RecommendationViewSet(viewsets.ViewSet):
    def list(self, request):
        calendar_id = request.query_params['calendar']
        calendar = Calendar.objects.get(pk=calendar_id)
        output_list = genie.recommend(calendar)
        serializer = RecommendationSerializer(instance=output_list, many=True)
        return Response(serializer.data)
