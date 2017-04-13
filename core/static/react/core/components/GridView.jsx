/*
* core/components/GridView.jsx
* Author: Rushy Panchal
* Date: April 5th, 2017
* Description: Renders an array of data as a list.
*/

var React = require('react'),
	Immutable = require('immutable');

function GridView(props) {
	/*
	* Required Props
	* 	Array data
	* 	Function t
	*   Number rows - number of rows to display (-1 means unlimited)
	*   Number cols - number of columns to display
	*
	* Optional Props
	* 	Function blankElement - element to output when blank
	*/
	var t = props.t;

	var rows = props.rows;
	if (rows == -1) rows = Math.ceil(props.data.length / props.cols);

	if (props.data.length || props.data.size) {
		var index = 0;
		var grid = new Array();
		for (var r=0; r<rows; r++) {
			var row = new Array();
			for (var c=0; c<props.cols; c++) {
				var elem = null;
				if (index < props.data.length) elem = props.data[index++];
				row.push(elem);
				}

			grid.push(row);
			}

		var columnSize = (12 / props.cols);
		columnSize = columnSize > 1 ? columnSize: 1;

		return <div className='grid-view'>
			{grid.map((row) => {
				return <div className='grid-row row' key={'grid-row-' + Math.random()}>
				{row.map((c, i, cs) => {
					return <span className={`grid-item ${columnSize}u`} key={'grid-item-' + Math.random()}>
					{c == null ? props.blankElement() : t(c, i, cs)}
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
	data: React.PropTypes.oneOfType([
		React.PropTypes.array,
		React.PropTypes.instanceOf(Immutable.List),
		]).isRequired,
	t: React.PropTypes.func.isRequired,
	rows: React.PropTypes.number,
	cols: React.PropTypes.number.isRequired,
	blankElement: React.PropTypes.func,	
	};

GridView.defaultProps = {
	blankElement: () => {<span></span>},
	rows: -1,
	};

module.exports = GridView;
