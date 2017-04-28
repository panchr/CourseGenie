/*
* core/components/Sandbox.jsx
* Author: Rushy sucks
* Date: April 28th, 2017
*/

var React = require('react');

import { DropTarget } from 'react-dnd';
import { List } from 'immutable';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
	ExpandingTabs = require('core/components/ExpandingTabs.jsx'),
	Sandbox = require('core/components/Sandbox.jsx'),
	Icon = require('core/components/Icon.jsx');

function Progresses(props) {
	return props.connectDropTarget(<div>
		<div className='topbtm-pad'></div>
		<div>Degree</div>
	</div>);
	}