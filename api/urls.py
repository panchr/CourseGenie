from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from api import views

router = DefaultRouter()
router.register(r'degrees', views.DegreeViewSet, base_name='degree')
router.register(r'majors', views.MajorViewSet, base_name='major')
router.register(r'tracks', views.TrackViewSet, base_name='track')
router.register(r'certificates', views.CertificateViewSet, base_name='certifcate')
router.register(r'calendars', views.CalendarViewSet, base_name='calendar')

app_name = 'api'
urlpatterns = [
    url(r'^', include(router.urls))
]

# urlpatterns = [
#     url(r'^degrees/$', views.DegreeList.as_view()),
#     url(r'^degrees/(?P<pk>[0-9]+)$', views.DegreeDetail.as_view()),
#     url(r'^majors/$', views.MajorList.as_view()),
#     url(r'^majors/(?P<pk>[0-9]+)$', views.MajorDetail.as_view()),
#     url(r'^certificates/$', views.CertificateList.as_view()),
#     url(r'^certificates/(?P<pk>[0-9]+)$', views.CertificateDetail.as_view()),
#     url(r'^tracks/$', views.TrackList.as_view()),
#     url(r'^tracks/(?P<pk>[0-9]+)$', views.TrackDetail.as_view()),
#     url(r'^courses/$', views.CourseList.as_view()),
#     url(r'^courses/(?P<pk>[0-9]+)$', views.CourseDetail.as_view()),
#     url(r'^crosslistings/$', views.CrossListingList.as_view()),
#     url(r'^crosslistings/(?P<pk>[0-9]+)$', views.CrossListingDetail.as_view()),
#     url(r'^requirements/$', views.RequirementList.as_view()),
#     url(r'^requirements/(?P<pk>[0-9]+)$', views.RequirementDetail.as_view()),
#     url(r'^profiles/$', views.ProfileList.as_view()),
#     url(r'^profiles/(?P<pk>[0-9]+)$', views.ProfileDetail.as_view()),
#     url(r'^records/$', views.RecordList.as_view()),
#     url(r'^records/(?P<pk>[0-9]+)$', views.RecordDetail.as_view()),
#     url(r'^calendars/$', views.CalendarList.as_view()),
#     url(r'^calendars/(?P<pk>[0-9]+)$', views.CalendarDetail.as_view()),
#     url(r'^progress/$', views.ProgressList.as_view()),
#     url(r'^progress/(?P<pk>[0-9]+)$', views.ProgressDetail.as_view()),
#     url(r'^areas/$', views.AreaList.as_view()),
#     url(r'^areas/(?P<pk>[0-9]+)$', views.AreaDetail.as_view()),
#     url(r'^departments/$', views.DepartmentList.as_view()),
#     url(r'^departments/(?P<pk>[0-9]+)$', views.DepartmentDetail.as_view()),
#     url(r'^preferences/$', views.PreferenceList.as_view()),
#     url(r'^preferences/(?P<pk>[0-9]+)$', views.PreferenceDetail.as_view()),
#     url(r'^semesters/$', views.SemesterList.as_view()),
#     url(r'^semesters/(?P<pk>[0-9]+)$', views.SemesterDetail.as_view()),
# ]

#urlpatterns = format_suffix_patterns(urlpatterns)