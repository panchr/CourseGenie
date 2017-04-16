from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import NotFound
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
