import re

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import NotFound, NotAcceptable, PermissionDenied
from rest_framework.response import Response

from api.serializers import *
from api import permissions
from core.models import *
from core.errors import *
from core import genie


COURSE_RE = re.compile(r'^(?P<dept>[A-Z]{3}) (?P<num>\d{3})(?P<letter>[A-Z]?)$')

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
    permission_classes = (permissions.ProgressAccess,)

class CalendarViewSet(viewsets.ModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = (permissions.CalendarAccess,)

    def update(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        genie.clear_cached_recommendations(obj.profile_id, obj.pk)
        return super(CalendarViewSet, self).update(request, pk, *args, **kwargs)

    def partial_update(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        genie.clear_cached_recommendations(obj.profile_id, obj.pk)
        return super(CalendarViewSet, self).partial_update(request, pk, *args, **kwargs)

    def perform_create(self, serializer):
        cal = serializer.save()
        genie.generate_semesters(cal)

    @detail_route(methods=['post', 'delete'], url_path='certificates')
    def modify_certificates(self, request, pk=None):
        calendar = self.get_object()
        certificate_id = request.query_params['cert_id']

        try:
            certificate = Certificate.objects.get(id=certificate_id)
        except Certificate.DoesNotExist:
            raise NotFound('Certificate "%s" not found.' % certificate_id)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if calendar.certificates.filter(id=certificate.id).exists():
                raise ContentError('Certificate "%s" already selected.' % certificate_id)

            calendar.certificates.add(certificate)
        elif request.method == 'DELETE':
            if not calendar.certificates.filter(id=certificate.id).exists():
                raise ContentError('Certificate "%s" not in this calendar.' % course_id)

            calendar.certificates.remove(certificate)

        genie.clear_cached_recommendations(calendar.profile_id, calendar.pk)
        return Response({'success': True})       

    @detail_route(methods=['post', 'delete'], url_path='sandbox')
    def modify_sandbox(self, request, pk=None):
        calendar = self.get_object()

        search_kwargs = {}
        course_name = ''
        if 'course_id' in request.query_params:
            course_name = request.query_params['course_id']
            search_kwargs['course_id'] = course_name
        elif 'short_name' in request.query_params:
            course_name = request.query_params['short_name']
            short_name = COURSE_RE.match(course_name)
            if not short_name:
                raise NotAcceptable(detail='short_name field does not match pattern.')

            search_kwargs['number'] = short_name.group('num')
            search_kwargs['department'] = short_name.group('dept')
            if short_name.group('letter'):
                search_kwargs['letter'] = short_name.group('letter')
        else:
            raise NotAcceptable(detail='short_name or course_id parameter required.')

        try:
            course = Course.objects.get(**search_kwargs)
        except Course.DoesNotExist:
            raise NotFound('Course "%s" not found.' % course_name)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if calendar.sandbox.filter(id=course.id).exists():
                raise ContentError('Course "%s" already in sandbox.' % course_name)

            calendar.sandbox.add(course)
        elif request.method == 'DELETE':
            if not calendar.sandbox.filter(id=course.id).exists():
                raise ContentError('Course "%s" not in sandbox.' % course_name)

            calendar.sandbox.remove(course)

        genie.clear_cached_recommendations(calendar.profile_id, calendar.pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

class PreferenceViewSet(viewsets.ModelViewSet):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer
    permission_classes = (permissions.PreferenceAccess,)

    def update(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        genie.clear_cached_recommendations(obj.profile_id)
        return super(PreferenceViewSet, self).update(request, pk, *args, **kwargs)

    def partial_update(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        genie.clear_cached_recommendations(obj.profile_id)
        return super(PreferenceViewSet, self).partial_update(request, pk, *args, **kwargs)

    @detail_route(methods=['post', 'delete'], url_path='bl-course')
    def modify_course(self, request, pk=None):
        pref = self.get_object()
        search_kwargs = {}
        course_name = ''

        if 'course_id' in request.query_params:
            course_name = request.query_params['course_id']
            search_kwargs['course_id'] = course_name
        else:
            course_name = request.query_params['short_name']
            short_name = COURSE_RE.match(course_name)
            if not short_name:
                raise NotAcceptable(detail='short_name field does not match pattern.')

            search_kwargs['number'] = short_name.group('num')
            search_kwargs['department'] = short_name.group('dept')
            if short_name.group('letter'):
                search_kwargs['letter'] = short_name.group('letter')

        try:
            course = Course.objects.get(**search_kwargs)
        except Course.DoesNotExist:
            raise NotFound('Course "%s" not found.' % course_name)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if pref.bl_courses.filter(id=course.id).exists():
                raise ContentError('Course "%s" already in blacklist.' % course_name)

            pref.bl_courses.add(course)
        elif request.method == 'DELETE':
            if not pref.bl_courses.filter(id=course.id).exists():
                raise ContentError('Course "%s" not in blacklist.' % course_name)

            pref.bl_courses.remove(course)

        genie.clear_cached_recommendations(pref.profile_id)
        return Response({'success': True})

    @detail_route(methods=['post', 'delete'], url_path='area')
    def modify_area(self, request, pk=None):
        pref = self.get_object()
        short_name = request.query_params['short_name']
        t = request.query_params['t']

        if t not in {'wl', 'bl'}:
            raise NotFound('Area "%s" not found for type "%s".' % (short_name, t))

        if t == 'wl':
            pref_list = pref.wl_areas
            other_list = pref.bl_areas
        else:
            pref_list = pref.bl_areas
            other_list = pref.wl_areas

        try:
            area = Area.objects.get(short_name=short_name)
        except Area.DoesNotExist:
            raise NotFound('Area %s not found.' % short_name)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if pref_list.filter(id=area.id).exists():
                raise ContentError('Area "%s" already in list.' % short_name)

            if other_list.filter(id=area.id).exists():
                raise ContentError('Area "%s" in opposing list.' % short_name)

            pref_list.add(area)
        elif request.method == 'DELETE':
            if not pref_list.filter(id=area.id).exists():
                raise ContentError('Area "%s" not in list.' % short_name)

            pref_list.remove(area)

        genie.clear_cached_recommendations(pref.profile_id)
        return Response({'success': True})

    @detail_route(methods=['post', 'delete'], url_path='dept')
    def modify_dept(self, request, pk=None):
        pref = self.get_object()
        short_name = request.query_params['short_name']
        t = request.query_params['t']

        if t not in {'wl', 'bl'}:
            raise NotFound('Department "%s" not found for type "%s".' % (short_name, t))

        if t == 'wl':
            pref_list = pref.wl_depts
            other_list = pref.bl_depts
        else:
            pref_list = pref.bl_depts
            other_list = pref.wl_depts

        try:
            dept = Department.objects.get(short_name=short_name)
        except Department.DoesNotExist:
            raise NotFound('Department "%s" not found.' % short_name)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if pref_list.filter(id=dept.id).exists():
                raise ContentError('Department "%s" already in list.' % short_name)

            if other_list.filter(id=dept.id).exists():
                raise ContentError('Department "%s" in opposing list.' % short_name)

            pref_list.add(dept)
        elif request.method == 'DELETE':
            if not pref_list.filter(id=dept.id).exists():
                raise ContentError('Department "%s" not in list.' % short_name)

            pref_list.remove(dept)

        genie.clear_cached_recommendations(pref.profile_id)
        return Response({'success': True})

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = (permissions.SemesterAccess,)

    @detail_route(methods=['post', 'delete'], url_path='course')
    def modify_course(self, request, pk=None):
        semester = self.get_object()

        search_kwargs = {}
        course_name = ''
        if 'course_id' in request.query_params:
            course_name = request.query_params['course_id']
            search_kwargs['course_id'] = course_name
        elif 'short_name' in request.query_params:
            course_name = request.query_params['short_name']
            short_name = COURSE_RE.match(course_name)
            if not short_name:
                raise NotAcceptable(detail='short_name field does not match pattern.')

            search_kwargs['number'] = short_name.group('num')
            search_kwargs['department'] = short_name.group('dept')
            if short_name.group('letter'):
                search_kwargs['letter'] = short_name.group('letter')
        else:
            raise NotAcceptable(detail='short_name or course_id parameter required.')

        try:
            course = Course.objects.get(**search_kwargs)
        except Course.DoesNotExist:
            raise NotFound('Course "%s" not found.' % course_name)

        if request.method == 'POST':
            # check if already there, and if so, raise 409
            if semester.courses.filter(id=course.id).exists():
                raise ContentError('Course "%s" already in semester.' % course_name)

            semester.courses.add(course)
        elif request.method == 'DELETE':
            if not semester.courses.filter(id=course.id).exists():
                raise ContentError('Course "%s" not in semester.' % course_name)

            semester.courses.remove(course)

        genie.clear_cached_recommendations(semester.calendar.profile_id)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

class ProgressViewSet(viewsets.ModelViewSet):
    filter_fields = ('calendar_id', 'requirement_id')
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer

    def update(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        genie.clear_cached_recommendations(obj.calendar.profile_id,
            obj.calendar_id)
        return super(ProgressViewSet, self).update(request, pk, *args, **kwargs)

    def partial_update(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        genie.clear_cached_recommendations(obj.calendar.profile_id,
            obj.calendar_id)
        return super(ProgressViewSet, self).partial_update(request, pk, *args, **kwargs)

# calculated on the stop
# need to add permissions
class RecommendationViewSet(viewsets.ViewSet):
    def list(self, request):
        calendar_id = request.query_params['calendar']
        calendar = Calendar.objects.get(pk=calendar_id)
        if calendar.profile.user != request.user:
            raise PermissionDenied(detail='Cannot access these recommendations.')
        output_list = genie.recommend(calendar)
        serializer = RecommendationSerializer(instance=output_list, many=True)
        return Response(serializer.data)
