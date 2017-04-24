/*
* core/components/ListView.jsx
* Author: Rushy Panchal
* Date: April 5th, 2017
* Description: Renders an array of data as a list.
*/

var React = require('react');

import { List } from 'immutable';

function ListView(props) {
	/*
	* Required Props
	* 	Array data
	* 	Function t
	*
	* Optional Props
	* 	String blankText - text when array is blank
	*/
	var t = props.t;

	if (props.data.length || props.data.size) {
		return <div className='list-view'>
			{props.data.map((x, i, xs) => {
				return <div className='list-item' key={'list-item-' + Math.random()}>
					{t(x, i, xs)}
					</div>
				})}
		</div>;
		}
	else {
		return <span>{props.blankText}</span>
		}
	}

ListView.propTypes = {
	data: React.PropTypes.oneOfType([
		React.PropTypes.array,
		React.PropTypes.instanceOf(List),
		]).isRequired,
	t: React.PropTypes.func.isRequired,
	blankText: React.PropTypes.string,	
	};

ListView.defaultProps = {
	blankText: '',
	};

module.exports = ListView;
