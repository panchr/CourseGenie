/*
* core/data.jsx
* Author: Rushy Panchal
* Date: April 9th, 2017
* Description: API to access data sources.
*/

var jQuery = require('jquery');

module.exports = {
	schedule: {
		getSemesters: function(callback) {
			var data = [
				{name: 'Spring 2018', courses: [
					{name: 'Advanced Programming Techniques', course_id: '1002',
					number: 333, letter: '', department: 'COS', 'area': 'QR'},
					{name: 'Computer Networks', course_id: '1003',
					number: 461, letter: '', department: 'COS', 'area': 'QR'},
					{name: 'The Environmental Nexus', course_id: '1004',
					number: 200, letter: 'A', department: 'ENV', 'area': 'STL'},
					{name: 'The Environmental Nexus', course_id: '1004',
					number: 200, letter: 'A', department: 'ENV', 'area': 'STL'}
					]},
				{name: 'Fall 2017', courses: [
					{name: 'Reasoning about Computation', course_id: '1005',
					number: 340, letter: '', department: 'COS', 'area': 'QR'},
					{name: 'Operating Systems', course_id: '1006',
					number: 318, letter: '', department: 'COS', 'area': 'QR'},
				]}
				];
			return callback(data);
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
