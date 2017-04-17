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
Icon = require('core/components/Icon.jsx');

function SemesterDisplay(props) {
	return props.connectDropTarget(<div>
		<div className='topbtm-pad'>
		<h2>{props.name}</h2></div>
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
			}} rows={2} cols={3} data={props.courses}
			blankElement={() =>
				<div className='course-blank'><Icon i='ios-plus-empty' className='large-icon'
				style={{color: 'green'}} /></div>} />
			<div className='topbtm-pad'></div>
			<div className='topbtm-pad'></div>
	</div>);
	}

SemesterDisplay.propTypes = {
	connectDropTarget: React.PropTypes.func.isRequired,
	onCourseAdd: React.PropTypes.func.isRequired,
	onCourseRemove: React.PropTypes.func.isRequired,
	name: React.PropTypes.string.isRequired,
	courses: React.PropTypes.array.isRequired,
	};

module.exports = DropTarget('course', {
	drop: (props, monitor, component) => {
		if (! monitor.didDrop()) {
			var data = monitor.getItem();
			props.onCourseAdd(data);
			data.onDragEnd();
			// Hack to make monitor recognize deletion, see:
			// https://github.com/react-dnd/react-dnd/issues/545
			monitor.internalMonitor.store.dispatch({type: "dnd-core/END_DRAG"});
			}
		}
	},
	(connect, monitor) => {
		return {
			connectDropTarget: connect.dropTarget(),
			};
		})(SemesterDisplay);
