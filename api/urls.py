from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from api import views

router = DefaultRouter()
# router.register(r'degrees', views.DegreeViewSet, base_name='degree')
# router.register(r'majors', views.MajorViewSet, base_name='major')
# router.register(r'tracks', views.TrackViewSet, base_name='track')
# router.register(r'certificates', views.CertificateViewSet, base_name='certifcate')
router.register(r'calendars', views.CalendarViewSet, base_name='calendar')
router.register(r'semesters', views.SemesterViewSet, base_name='semester')
# router.register(r'areas', views.AreaViewSet, base_name='area')
# router.register(r'departments', views.DepartmentViewSet, base_name='department')
# router.register(r'courses', views.CourseViewSet, base_name='course')
# router.register(r'crosslistings', views.CrossListingViewSet, base_name='crosslisting')
# router.register(r'requirements', views.RequirementViewSet, base_name='requirement')
# router.register(r'nestedreqs', views.NestedReqViewSet, base_name='nestedreq')
router.register(r'recommendations', views.RecommendationViewSet,
	base_name='recommendation')
router.register(r'preferences', views.PreferenceViewSet,
	base_name='preference')
router.register(r'progresses', views.ProgressViewSet, base_name='progress')

app_name = 'api'
urlpatterns = [
    url(r'^', include(router.urls))
]
