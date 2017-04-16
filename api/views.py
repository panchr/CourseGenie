from core.models import *
from api.serializers import *
from rest_framework import viewsets
from rest_framework.decorators import detail_route
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

class ProgressViewSet(viewsets.ModelViewSet):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer

# calculated on the stop
class RecommendationViewSet(viewsets.ViewSet):
    def list(self, request):
        calendar_id = request.query_params['calendar']
        calendar = Calendar.objects.get(pk=calendar_id)
        output_list = genie.recommend(calendar)
        serializer = RecommendationSerializer(instance=output_list)
        return Response(serializer.data)
