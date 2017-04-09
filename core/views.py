# core/views.py
# CourseGenie

import urllib2
import json

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse

from core.models import *
from core import genie

# Create your views here.
class IndexView(TemplateView):
	template_name = 'core/index.html'

class TranscriptView(LoginRequiredMixin, TemplateView):
	template_name = 'core/form-transcript.html'

	def get_context_data(self, **kwargs):
		context = super(TranscriptView, self).get_context_data(**kwargs)
		page_url = self.request.build_absolute_uri(reverse('core:transcript'))
		service_url = '{base}?redirect={redirect}'.format(
			base=settings.TRANSCRIPT_API_URL, redirect=page_url)
		context['transcript_service_url'] = service_url
		context['transcript_url'] = '{}/transcript/?ticket='.format(settings.TRANSCRIPT_API_URL)
		context['form_action'] = page_url

		user = self.request.user
		context['data'] = json.dumps({
			'existing_courses': user.profile.course_list(),
			'user': {
				'first_name': user.first_name,
				'last_name': user.last_name,
				},
			'graduation_year': user.profile.year
			})

		return context

	def post(self, request):
		data = json.loads(request.POST['data'])
		user = request.user
		genie.store_manual(user, data['courses'])
		user.first_name = data['user']['first_name']
		user.last_name = data['user']['last_name']
		user.profile.year = data['graduation_year']
		user.profile.submitted = True
		user.save()
		user.profile.save()

		return render(request, 'core/data.html', {'data': data})

class DashboardView(LoginRequiredMixin, TemplateView):
	template_name = 'core/dashboard.html'

	def get(self, request):
		user = request.user
		if user.profile.submitted:
			return super(DashboardView, self).get(request)

		return redirect('core:transcript')
