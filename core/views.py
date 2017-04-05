# core/views.py
# CourseGenie

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import *

# Create your views here.
class IndexView(LoginRequiredMixin, TemplateView):
	template_name = 'core/index.html'
