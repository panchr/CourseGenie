/*
* core/components/Sandbox.jsx
* Author: Rushy Panchal
* Date: April 28th, 2017
*/

var React = require('react');

import { DropTarget } from 'react-dnd';
import { List } from 'immutable';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
	GridView = require('core/components/GridView.jsx'),
	Icon = require('core/components/Icon.jsx');

function Sandbox(props) {
	return props.connectDropTarget(<div>
		<div className='topbtm-pad'></div>
		<br/>
		<div className='grid-pad'>
		<GridView t={(c, i) => {
			return <div className='course-list'>
					<div className='row'>
				<div className='11u'><CourseDisplay {...c} extended={true}/></div>
				<div className='1u no-left-padding'>
					<Icon i='ios-close-empty'
						className='btn' style={{color: 'LightSlateGray'}}
						onClick={() => {props.onCourseRemove(c, i)}} />
				</div>
			</div>
			</div>;
		}} cols={3} minRows={2} data={props.courses}
			blankElement={() =>
				<div className='course-blank'>
				<Icon i='ios-plus-empty' className='large-icon course-plus' />
				</div>} /></div>
		<div className='topbtm-pad'></div>
		<div className='topbtm-pad'></div>
	</div>);
	}

Sandbox.propTypes = {
	connectDropTarget: React.PropTypes.func.isRequired,
	onCourseAdd: React.PropTypes.func.isRequired,
	onCourseRemove: React.PropTypes.func.isRequired,
	courses: React.PropTypes.array.isRequired,
	};

module.exports = DropTarget('course', {
	drop: (props, monitor, component) => {
		var data = monitor.getItem();

		if (! monitor.didDrop()) {
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
		})(Sandbox);
