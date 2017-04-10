from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^degrees/$', views.degree_list),
    url(r'^degrees/(?P<pk>[0-9]+)$', views.degree_detail),
    url(r'^majors/$', views.major_list),
    url(r'^majors/(?P<pk>[0-9]+)$', views.major_detail),
    url(r'^certificates/$', views.certificate_list),
    url(r'^certificates/(?P<pk>[0-9]+)$', views.certificate_detail),
    url(r'^tracks/$', views.track_list),
    url(r'^tracks/(?P<pk>[0-9]+)$', views.track_detail),
    url(r'^courses/$', views.course_list),
    url(r'^courses/(?P<pk>[0-9]+)$', views.course_detail),
    url(r'^crosslistings/$', views.crosslisting_list),
    url(r'^crosslistings/(?P<pk>[0-9]+)$', views.crosslisting_detail),
    url(r'^requirements/$', views.requirement_list),
    url(r'^requirements/(?P<pk>[0-9]+)$', views.requirement_detail),
    url(r'^profiles/$', views.profile_list),
    url(r'^profiles/(?P<pk>[0-9]+)$', views.profile_detail),
    url(r'^records/$', views.record_list),
    url(r'^records/(?P<pk>[0-9]+)$', views.record_detail),
    url(r'^calendars/$', views.calendar_list),
    url(r'^calendars/(?P<pk>[0-9]+)$', views.calendar_detail),
    url(r'^progress/$', views.progress_list),
    url(r'^progress/(?P<pk>[0-9]+)$', views.progress_detail),
    url(r'^areas/$', views.area_list),
    url(r'^areas/(?P<pk>[0-9]+)$', views.area_detail),
    url(r'^departments/$', views.department_list),
    url(r'^departments/(?P<pk>[0-9]+)$', views.department_detail),
    url(r'^preferences/$', views.preference_list),
    url(r'^preferences/(?P<pk>[0-9]+)$', views.preference_detail),
    url(r'^semesters/$', views.semester_list),
    url(r'^semesters/(?P<pk>[0-9]+)$', views.semester_detail),
]

#urlpatterns = format_suffix_patterns(urlpatterns)