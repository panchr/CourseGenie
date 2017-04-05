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

class TranscriptView(LoginRequiredMixin, TemplateView):
	template_name = 'core/transcript.html'

	def get_context_data(self, **kwargs):
		context = super(TranscriptView, self).get_context_data(**kwargs)

		ticket = self.request.GET['ticket']
		if not ticket:
			# need to raise an error here/display error message
			return False

		url='{base}/transcript/?ticket={ticket}'.format(
			base=settings.TRANSCRIPT_API_URL, ticket=ticket)
		# User-Agent is required; otherwise, TranscriptAPI denies access.
		request = urllib2.Request(url, headers={'User-Agent': 'CourseGenie/0.1'})
		response = urllib2.urlopen(request)
		transcript_data = json.load(response)

		# store user's transcript data

		context['transcript'] = transcript_data
		return context
