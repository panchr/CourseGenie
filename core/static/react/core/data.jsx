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
			if (response.responseJSON && response.responseJSON.error) {
				msg = response.responseJSON.error;
				}
			handler(msg);
			};
		},

	calendar: {
		getSemesters: function(id, callback) {
			return jQuery.get(dashboard_data.calendar.url(id))
				.done((data) => callback(data.semesters))
				.fail(shared.errorHandler);
			},

		addToSemester: function(semester_id, course, callback) {
			setup_ajax_csrf();
			return jQuery.post(dashboard_data.calendar.semesterCourseUrl(semester_id,
				course.course_id))
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			},

		removeFromSemester: function(semester_id, course, callback) {
			setup_ajax_csrf();
			return jQuery.ajax(dashboard_data.calendar.semesterCourseUrl(semester_id,
				course.course_id), {method: 'DELETE'})
				.done((data) => callback(data))
				.fail(shared.errorHandler);
			}
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

	requirements: {
		degree: function(callback) {
			var data = [
				{name: 'Physics', t: 'physics', number: 2, notes: '', object_id: 1,
				courses: [
					{name: 'General Physics I', course_id: '1005', number: 103,
					letter: '', department: 'PHY', 'area': 'QR'},
					{name: 'General Physics II', course_id: '1003',
					number: 104, letter: '', department: 'PHY', 'area': 'QR'}
					]},
				{'name': 'Computing', t: 'cs', number: 1, notes: '', object_id: 1,
				courses: [
					{name: 'Algorithms and Data Structures', course_id: '1011',
					number: 226, department: 'COS', letter: '', area: ''},
					{name: 'Introduction to Programming Systems', course_id: '1010',
					number: 217, department: 'COS', letter: '', area: ''},
					{name: 'Introduction to Computer Science', course_id: '1012',
					number: 126, department: 'COS', letter: '', area: 'QR'},
					]}
				];
			return callback(data);
			},
		},
	};
