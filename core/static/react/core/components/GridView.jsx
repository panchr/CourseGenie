/*
* core/components/GridView.jsx
* Author: Rushy Panchal
* Date: April 5th, 2017
* Description: Renders an array of data as a list.
*/

var React = require('react');

function GridView(props) {
	/*
	* Required Props
	* 	Array data
	* 	Function t
	*   Number rows - number of rows to display
	*   Number cols - number of columns to display
	*
	* Optional Props
	* 	Function blankElement - element to output when blank
	*/
	var t = props.t;

	if (props.data.length) {
		var index = 0;
		var grid = new Array();
		for (var r=0; r<props.rows; r++) {
			var row = new Array();
			for (var c=0; c<props.cols; c++) {
				var elem = null;
				if (index < props.data.length) elem = props.data[index++];
				row.push(elem);
				}

			grid.push(row);
			}

		return <div className='grid-view'>
			{grid.map((row) => {
				return <div className='grid-row' key={'grid-row-' + Math.random()}>
				{row.map((c) => {
					return <span className="grid-item" key={'grid-item-' + Math.random()}>
					{c == null ? props.blankElement() : t(c)}
					</span>;
					})}
				</div>;
				})}
		</div>;
		}
	else {
		return <div>{props.blankElement()}</div>;
		}
	}

GridView.propTypes = {
	data: React.PropTypes.array.isRequired,
	t: React.PropTypes.func.isRequired,
	rows: React.PropTypes.number.isRequired,
	cols: React.PropTypes.number.isRequired,
	blankElement: React.PropTypes.func,	
	};

GridView.defaultProps = {
	blankElement: () => {<span></span>},
	};

module.exports = GridView;
