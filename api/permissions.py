# permissions.py
# May 1st, 2017

from rest_framework import permissions

class CalendarAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.profile.user == request.user

class SemesterAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.calendar.profile.user == request.user

class PreferenceAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.profile.user == request.user

class ProgressAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.calendar.profile.user == request.user