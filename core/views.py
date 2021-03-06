# core/views.py
# CourseGenie

import urllib2
import json
import base64

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone

from core.models import *
from core import genie

# Create your views here.
class IndexView(TemplateView):
	template_name = 'core/index.html'

class QuestionView(LoginRequiredMixin, TemplateView):
	template_name = 'core/questions.html'

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
		context['majors'] = json.dumps(list(Major.objects.all().values(
			'short_name', 'name', 'id')))

		user = self.request.user
		context['data'] = json.dumps({
			'existing_courses': user.profile.course_list(),
			'user': {
				'first_name': user.first_name,
				'last_name': user.last_name,
				},
			'graduation_year': user.profile.year,
			'submitted': user.profile.submitted,
			})

		return context

	def post(self, request):
		data = json.loads(request.POST['data'])
		user = request.user
		genie.store_manual(user, data['courses'])
		user.first_name = data['user']['first_name']
		user.last_name = data['user']['last_name']
		user.profile.year = int(data['graduation_year'])

		if not (user.profile.submitted
			and Calendar.objects.filter(profile=user.profile).exists()):
			calendar = Calendar.objects.create(profile=user.profile,
				degree_id=1, major_id=int(data['major']), name='Default Calendar')
			genie.generate_semesters(calendar)

		user.profile.submitted = True
		user.save()
		user.profile.save()

		genie.clear_cached_recommendations(user.profile.id)
		return redirect('core:dashboard')

class DashboardView(LoginRequiredMixin, TemplateView):
	template_name = 'core/dashboard.html'

	def get_context_data(self, **kwargs):
		context = super(DashboardView, self).get_context_data(**kwargs)
		user = self.request.user
		user_calendars = list(Calendar.objects.filter(profile=user.profile.id).values('id', 'name'))
		context['user_calendars'] = to_js(user_calendars)
		context['profile_id'] = user.profile.id
		context['preference_id'] = user.profile.preference.id
		context['majors'] = to_js(list(Major.objects.all().values(
			'short_name', 'name', 'id')))
		context['tracks'] = to_js(list(Track.objects.all().values(
			'short_name', 'name', 'id', 'major_id')))
		context['certificates'] = to_js(list(Certificate.objects.all().values(
			'short_name', 'name', 'id')))

		return context

	def get(self, request):
		user = request.user
		if user.profile.submitted:
			return super(DashboardView, self).get(request)

		return redirect('core:transcript')

class PreferenceView(LoginRequiredMixin, TemplateView):
	template_name = 'core/form-preferences.html'

	def get_context_data(self, **kwargs):
		context = super(PreferenceView, self).get_context_data(**kwargs)
		context['preference_id'] = self.request.user.profile.preference.id

		return context

def to_js(d):
	return base64.encodestring(json.dumps(d)).replace('\n', '')
