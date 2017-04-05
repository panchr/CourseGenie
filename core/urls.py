# core/urls.py
# CourseGenie
# Author: Rushy Panchal
# Date: March 18th, 2017

from django.conf.urls import url

from core import views

app_name = 'core'
urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^dashboard/$', views.DashboardView.as_view(), name='dashboard'),
	url(r'^post-transcript/$', views.TranscriptView.as_view(),
		name='transcript-upload'),
	]
