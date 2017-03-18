# core/urls.py
# CourseVision
# Author: Rushy Panchal
# Date: March 18th, 2017

from django.conf.urls import url

from core import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view()),
	]
