/*
* core/components/RecommendationDisplay.jsx
* Author: Rushy Panchal
* Date: April 12th, 2017
* Description: Provides a list of rendered data.
*/

var React = require('react');

import { DragSource } from 'react-dnd';

function RecommendationDisplay(props) {
	return props.connectDragSource(<div className='suggestion-display'>
		<div className='12u'>
			<div>{props.course.short_name} ({props.course.term_display})</div>
			<div>{props.course.name}</div>
			<div><font color='CadetBlue'>Reason: {props.reason}</font></div>
		</div>
	</div>);
	}

RecommendationDisplay.propTypes = {
	connectDragSource: React.PropTypes.func.isRequired,
	onDragEnd: React.PropTypes.func.isRequired,
	course: React.PropTypes.object.isRequired,
	reason: React.PropTypes.string.isRequired,
	};

module.exports = DragSource('course', {
	beginDrag: (props, monitor, component) => props,
	},
	(connect, monitor) => {
		return {
			connectDragSource: connect.dragSource(),
		};
		})(RecommendationDisplay);
