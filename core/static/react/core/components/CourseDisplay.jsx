/*
* core/components/CourseDisplay.jsx
* Author: Rushy Panchal
* Date: April 5th, 2017
* Description: Provides a list of rendered data.
*/

var React = require('react');

function CourseDisplay(props) {
	return (<span>{props.department} {props.number}</span>);
	}

CourseDisplay.propTypes = {
	department: React.PropTypes.string.isRequired,
	number: React.PropTypes.string.isRequired,
	}

module.exports = CourseDisplay;
