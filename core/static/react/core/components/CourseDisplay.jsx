/*
* core/components/CourseDisplay.jsx
* Author: Rushy Panchal
* Date: April 5th, 2017
* Description: Provides a list of rendered data.
*/

var React = require('react');

function CourseDisplay(props) {
	if (props.extended) {
		// maybe display area as badge, color-coded?
		return (<span className='course-display'>
			<div>{props.department} {props.number}{props.letter}
				{props.area == '' ? null : ` (${props.area})` }</div>
			<div>{props.name}</div>
		</span>);
		}
	else return <span className='course-display'>{props.department} {props.number}</span>;
	}

CourseDisplay.propTypes = {
	extended: React.PropTypes.bool,
	department: React.PropTypes.string.isRequired,
	number: React.PropTypes.oneOfType([
		React.PropTypes.string,
		React.PropTypes.number,
		]).isRequired,
	letter: React.PropTypes.string,
	name: React.PropTypes.string,
	area: React.PropTypes.string,
	};

CourseDisplay.defaultProps = {
	extended: false,
	letter: '',
	name: '',
	area: '',
	};

module.exports = CourseDisplay;
