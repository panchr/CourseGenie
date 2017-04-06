# core/views.py
# CourseGenie
import urllib2
import json

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import *
from django.conf import settings
from django.core.urlresolvers import reverse

# Create your views here.
class IndexView(TemplateView):
	template_name = 'core/index.html'

class DashboardView(LoginRequiredMixin, TemplateView):

	def get_template_names(self):
		user = self.request.user
		profile = Profile.objects.get(user=user)
		records = Record.objects.filter(profile=profile)
		if records.count() == 0:
			template_name = 'core/form-transcript.html'
		else:
			template_name = 'core/dashboard.html'

		return [template_name]
		
	def get_context_data(self, **kwargs):
		context = super(DashboardView, self).get_context_data(**kwargs)
		service_url = '{base}?redirect={redirect}'.format(
			base=settings.TRANSCRIPT_API_URL,
			redirect=self.request.build_absolute_uri(
				reverse('core:dashboard')))
		context['transcript_service_url'] = service_url
		context['transcript_url'] = '{}/transcript/?ticket='.format(settings.TRANSCRIPT_API_URL)
		return context
