from core.models import *
from api.serializers import *
from rest_framework import generics, viewsets
from rest_framework.decorators import detail_route

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

class CalendarViewSet(viewsets.ModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer

# class DegreeList(generics.ListCreateAPIView):
#     queryset = Degree.objects.all()
#     serializer_class = DegreeSerializer

# class DegreeDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Degree.objects.all()
#     serializer_class = DegreeSerializer

class MajorList(generics.ListCreateAPIView):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer

class MajorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer

class CertificateList(generics.ListCreateAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

class CertificateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

class TrackList(generics.ListCreateAPIView):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

class TrackDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CrossListingList(generics.ListCreateAPIView):
    queryset = CrossListing.objects.all()
    serializer_class = CrossListingSerializer

class CrossListingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CrossListing.objects.all()
    serializer_class = CrossListingSerializer

class RequirementList(generics.ListCreateAPIView):
    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer

class RequirementDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer

class NestedReqList(generics.ListCreateAPIView):
    queryset = NestedReq.objects.all()
    serializer_class = NestedReqSerializer

class NestedReqDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NestedReq.objects.all()
    serializer_class = NestedReqSerializer

class ProfileList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class RecordList(generics.ListCreateAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

class RecordDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

class CalendarList(generics.ListCreateAPIView):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer

class CalendarDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer

class ProgressList(generics.ListCreateAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer

class ProgressDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer

class AreaList(generics.ListCreateAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class AreaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class DepartmentList(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DepartmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class PreferenceList(generics.ListCreateAPIView):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer

class PreferenceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer

class SemesterList(generics.ListCreateAPIView):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

class SemesterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
