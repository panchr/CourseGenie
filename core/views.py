from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class IndexView(TemplateView):
	template_name = 'core/index.html'

class DashboardView(LoginRequiredMixin, TemplateView):
	template_name = 'core/form-transcript.html'
