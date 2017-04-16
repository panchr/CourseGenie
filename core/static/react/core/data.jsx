/*
* core/data.jsx
* Author: Rushy Panchal
* Date: April 9th, 2017
* Description: API to access data sources.
*/

var jQuery = require('jquery');

var shared = {};

module.exports = {
	installErrorHandler: function(handler) {
		shared.errorHandler = handler;
		},

	calendar: {
		getSemesters: function(id, callback) {
			return jQuery.get(calendar_url(id))
				.done((data) => callback(data.semesters))
				.fail(shared.errorHandler);
			},

		addToSemester: function(semester_id, course, callback) {
			
			}
		},

	recommendations: {
		get: function(callback) {
			var data = [
			{'course_id': '123456',  'name': 'Introduction to Macroeconomics',
				'score': 3, 'short_name': 'ECO 101', 'department': 'ECO',
				'number': 101, 'letter': '',
				'reason': 'Distribution requirement: ER.'},
			{'course_id': '123457',  'name': 'Computer Networks', 'score': 4,
				'short_name': 'COS 461', 'department': 'COS', 'number': 461,
				'letter': '',
				'reason': 'Systems Requirement'},
			];
			return callback(data);
			},

		dismiss: function(id, callback=(e) => null) {
			// dismiss recommendation with ID
			console.log('Dismissing', id);
			return callback(null);
			}
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
