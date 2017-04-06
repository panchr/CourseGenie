/*
* core/components/ListView.jsx
* Author: Rushy Panchal
* Date: April 5th, 2017
* Description: Renders an array of data as a list.
*/

var React = require('react');

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

	if (props.data.length) {
		return <div className='list-view'>
			{props.data.map((x) => {
				return <div className='list-item' key={'list-item-' + Math.random()}>
					{t(x)}
					</div>
				})}
		</div>;
		}
	else {
		return <span>{props.blankText}</span>
		}
	}

ListView.propTypes = {
	data: React.PropTypes.array.isRequired,
	t: React.PropTypes.func.isRequired,
	blankText: React.PropTypes.string,	
	};

ListView.defaultProps = {
	blankText: '',
	};

module.exports = ListView;
