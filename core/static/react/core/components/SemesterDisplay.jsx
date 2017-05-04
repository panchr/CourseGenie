/*
* core/components/SemesterDisplay.jsx
* Author: Rushy Panchal
* Date: April 13th, 2017
* Description: Renders a single semester.
*/

var React = require('react');

import { DropTarget } from 'react-dnd';
import { List } from 'immutable';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
	GridView = require('core/components/GridView.jsx'),
	Icon = require('core/components/Icon.jsx'),
	utils = require('core/utils.jsx');

function SemesterDisplay(props) {
	return props.connectDropTarget(<div>
		<div className='topbtm-pad'>
		<h2>{props.term_display} {props.year}</h2></div>
		<br/>
		<GridView t={(c, i) => {
			return <div className='course-list'>
					<div className='row'>
				<div className='11u'><CourseDisplay {...c} extended={true} /></div>
				<div className='1u no-left-padding'>
					<Icon i='ios-close-empty'
						className='btn' style={{color: 'LightSlateGray'}}
						onClick={() => {props.onCourseRemove(c, i)}} />
				</div>
			</div>
			</div>;
			}} rows={2} cols={3} minRows={2} data={props.courses}
			blankElement={() =>
				<div className='course-blank btn course-color' onClick={props.onPlusClick}>
				<Icon i='ios-plus-empty' className='large-icon course-plus' />
				</div>} />
			<br/>
	</div>);
	}

SemesterDisplay.propTypes = {
	connectDropTarget: React.PropTypes.func.isRequired,
	onCourseAdd: React.PropTypes.func.isRequired,
	onCourseRemove: React.PropTypes.func.isRequired,
	onPlusClick: React.PropTypes.func.isRequired,
	onError: React.PropTypes.func.isRequired,
	term_display: React.PropTypes.string.isRequired,
	year: React.PropTypes.number.isRequired,
	courses: React.PropTypes.array.isRequired,
	maxSize: React.PropTypes.number,
	};

SemesterDisplay.defaultProps = {
	maxSize: -1,
	};

module.exports = DropTarget('course', {
	drop: (props, monitor, component) => {
		var data = monitor.getItem();

		// These checks must be performed here (instead of in the canDrop() method)
		// because we only want to display an error message on drop, not on hover.
		if (props.maxSize != -1 && props.maxSize <= utils.length(props.courses)) {
			props.onError({
				header: `${props.term_display} ${props.year}`,
				t: 'error',
				message: `Cannot add more than ${props.maxSize} courses.`});
			}
		else if (data.course.term != props.term &&
			(data.course.term_display == 'Fall' || data.course.term_display == 'Spring')) {
			props.onError({
				header: `${props.term_display} ${props.year}`,
				t: 'error',
				message: `Cannot add ${data.course.term_display}-only course (${data.course.short_name}) to ${props.term_display} semester.`
				});
			}
		else if (! monitor.didDrop()) {
			props.onCourseAdd(data.course);
			data.onDragEnd();
			}
		// Hack to make monitor recognize deletion, see:
		// https://github.com/react-dnd/react-dnd/issues/545
		monitor.internalMonitor.store.dispatch({type: "dnd-core/END_DRAG"});
		},
	},
	(connect, monitor) => {
		return {
			connectDropTarget: connect.dropTarget(),
			};
		})(SemesterDisplay);
