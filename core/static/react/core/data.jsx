/*
* core/data.jsx
* Author: Rushy Panchal
* Date: April 9th, 2017
* Description: API to access data sources.
*/

var jQuery = require('jquery');

var shared = {};

function setup_ajax_csrf() {
	/*
	* Set up AJAX requests to use CSRF, if necessary.
	* Gets the CSRF token from the 'csrftoken' cookie.
	*
	* Adapted from: https://docs.djangoproject.com/en/1.9/ref/csrf/#ajax.
	*/
	// var csrf_token = Cookies.get('csrftoken');
	jQuery.ajaxSetup({
		beforeSend: function(xhr, settings) {
			/* The CSRF token should only be set if the method is not a safe
			method. */
			if (! (this.crossDomain ||
				/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type))) {
				xhr.setRequestHeader('X-CSRFToken', window._csrf_token);
				}
			}
		});
	}

module.exports = {
	installErrorHandler: function(handler) {
		shared.errorHandler = (response, msg, error) => {
			var msg = response.responseText;
			if (response.responseJSON) {
				if (response.responseJSON.error) msg = response.responseJSON.error;
				else if (response.responseJSON.detail) msg = response.responseJSON.detail;
				}
			handler(msg);
			};
		},

	calendar: {
		getData: function(id, callback) {
			return jQuery.get(dashboard_data.calendar.url(id))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		create: function(data, callback=() => null) {
			return jQuery.post(dashboard_data.calendar.createUrl, data)
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		delete: function(id, callback=() => null) {
			return jQuery.ajax(dashboard_data.calendar.url(id), {method: 'DELETE'})
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		saveSettings: function(id, data, callback=()=>null) {
			return jQuery.ajax(dashboard_data.calendar.url(id),
				{method: 'PATCH', data: data})
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		addToSemester: function(semester_id, course, callback) {
			setup_ajax_csrf();
			return jQuery.post(dashboard_data.calendar.semesterCourseUrl(semester_id,
				course.course_id))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		addToSemesterByCourseName: function(semester_id, course_short_name, callback) {
			setup_ajax_csrf();
			return jQuery.post(dashboard_data.calendar.semesterShortCourseUrl(semester_id,
				course_short_name))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		removeFromSemester: function(semester_id, course, callback) {
			setup_ajax_csrf();
			return jQuery.ajax(dashboard_data.calendar.semesterCourseUrl(semester_id,
				course.course_id), {method: 'DELETE'})
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		addToSandbox: function(id, course, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.post(dashboard_data.calendar.sandboxUrl(id,
				course.course_id))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		addToSandboxShort: function(id, short_name, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.post(dashboard_data.calendar.sandboxShortUrl(id,
				short_name))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		removeFromSandbox: function(id, course, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.ajax(dashboard_data.calendar.sandboxUrl(id,
				course.course_id), {method: 'DELETE'})
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		getProgress: function(id, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.get(dashboard_data.calendar.progressUrl(id))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		getSingleProgress: function(id, req_id, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.get(dashboard_data.calendar.singleProgressByRequirementUrl(id, req_id))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		setSingleProgress: function(id, data, callback=(e) => null, fail=(e)=>null) {
			setup_ajax_csrf();
			return jQuery.ajax(dashboard_data.calendar.singleProgressUrl(id),
				{method: 'PATCH', data: data})
				.done((data) => callback(data))
				.fail((response, msg, error) => {
					if (! fail(response, msg, error))
						shared.errorHandler(response, msg, error);
					});
			},

		addCertificate: function(id, cert_id, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.post(dashboard_data.calendar.certificateUrl(id, cert_id))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		removeCertificate: function(id, cert_id, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.ajax(dashboard_data.calendar.certificateUrl(id, cert_id),
				{method: 'DELETE'})
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},
		},

	recommendations: {
		get: function(calendar_id, callback) {
			return jQuery.get(dashboard_data.recommendations.url(calendar_id))
				.done(callback)
				.fail(shared.errorHandler);
			},

		dismiss: function(id, callback=(e) => null) {
			// dismiss recommendation with ID
			setup_ajax_csrf();
			return jQuery.post(dashboard_data.recommendations.blacklistUrl(id))
				.done(callback)
				.fail(shared.errorHandler);
			},
		},

	preferences: {
		get: function(callback=(e) => null) {
			return jQuery.get(preference_data.urls.preference())
				.done(callback)
				.fail(shared.errorHandler);
			},

		patch: function(data, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.ajax(preference_data.urls.preference(),
				{method: 'PATCH', data: data})
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		bl_course: function(course, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.post(preference_data.urls.bl_course(course))
				.done(callback)
				.fail(shared.errorHandler);
			},

		bl_dept: function(dept, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.post(preference_data.urls.bl_dept(dept))
				.done(callback)
				.fail(shared.errorHandler);
			},

		wl_dept: function(dept, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.post(preference_data.urls.wl_dept(dept))
				.done(callback)
				.fail(shared.errorHandler);
			},

		bl_area: function(area, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.post(preference_data.urls.bl_area(area))
				.done(callback)
				.fail(shared.errorHandler);
			},

		wl_area: function(area, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.post(preference_data.urls.wl_area(area))
				.done(callback)
				.fail(shared.errorHandler);
			},

		del_bl_course: function(course, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.ajax(preference_data.urls.bl_course(course),
				{method: 'DELETE'})
				.done(callback)
				.fail(shared.errorHandler);
			},

		del_bl_dept: function(dept, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.ajax(preference_data.urls.bl_dept(dept),
				{method: 'DELETE'})
				.done(callback)
				.fail(shared.errorHandler);
			},

		del_wl_dept: function(dept, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.ajax(preference_data.urls.wl_dept(dept),
				{method: 'DELETE'})
				.done(callback)
				.fail(shared.errorHandler);
			},

		del_bl_area: function(area, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.ajax(preference_data.urls.bl_area(area),
				{method: 'DELETE'})
				.done(callback)
				.fail(shared.errorHandler);
			},

		del_wl_area: function(area, callback=(e) => null) {
			setup_ajax_csrf();
			return jQuery.ajax(preference_data.urls.wl_area(area),
				{method: 'DELETE'})
				.done(callback)
				.fail(shared.errorHandler);
			},
		},
	};
