/*
* core/components/SemesterDisplay.jsx
* Author: Rushy Panchal
* Date: April 13th, 2017
* Description: Renders a single semester.
*/

var React = require('react');

import { DropTarget } from 'react-dnd';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
GridView = require('core/components/GridView.jsx'),
Icon = require('core/components/Icon.jsx');

function SemesterDisplay(props) {
	return <div>
		<h2>{props.name}</h2>
		<GridView t={(c) => {
			return <CourseDisplay {...c} extended={true} />;
			}} rows={2} cols={3} data={props.courses}
			blankElement={() =>
				<Icon i='ios-plus' className='large-icon'
				style={{color: 'green'}} />} />
	</div>;
	}

SemesterDisplay.propTypes = {
	name: React.PropTypes.string.isRequired,
	courses: React.PropTypes.array.isRequired,
	};

module.exports = DropTarget('course', {
	drop: (props) => {
		console.log(props);
		}
	},
	(connect, monitor) => new Object())(SemesterDisplay);
