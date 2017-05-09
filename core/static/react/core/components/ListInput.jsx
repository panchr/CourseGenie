/*
* core/components/ListInput.jsx
* Author: Rushy Panchal
* Date: April 20th, 2017
* Description: Renders an array of data as a list which can be added onto.
*/

var React = require('react');

var GridView = require('core/components/GridView.jsx'),
	Icon = require('core/components/Icon.jsx');

import { List } from 'immutable';

class ListInput extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			data: new List(props.data),
			};

		this.addElement = this.addElement.bind(this);
		this.removeElement = this.removeElement.bind(this);
		}

	componentWillReceiveProps(newProps) {
		if (newProps.data != this.state.data) {
			this.setState({data: newProps.data});
			}
		}

	addElement() {
		var data = this.props.getInput();
		if (data == undefined || data == null) return;
		this.setState({data: this.state.data.push(data)},
			() => this.props.onAdd(data));
		}

	removeElement(index) {
		var removed_data = this.state.data.get(index);
		this.props.onDelete(removed_data, index)
		this.setState({data: this.state.data.remove(index)});
		}

	getValues() {
		return this.state.data;
		}

	render() {
		return <div>
			<div className='row'>
				{this.props.children}
			</div>
			<div className="row">
				<div className="12u title">
					<div className='center-parent' style={{width: '30%'}}>
						<a className="button-add fit btn" onClick={this.addElement}>Add</a>
					</div>
				</div>
			</div>
			<GridView t={(e, i) => {
				return <div className='course-entry'>
					{this.props.t(e, i)} &nbsp;
					<Icon i='ios-close-empty' style={{color: 'LightSlateGray'}} className='btn'
						onClick={() => {this.removeElement(i)}} />
				</div>
				}} data={this.state.data} cols={this.props.cols}
				blankText={this.props.blankText} />
		</div>;
		}
	}

ListInput.propTypes = {
	data: React.PropTypes.oneOfType([
		React.PropTypes.array,
		React.PropTypes.instanceOf(List),
		]).isRequired,
	t: React.PropTypes.func.isRequired,
	getInput: React.PropTypes.func.isRequired,
	cols: React.PropTypes.number,
	blankText: React.PropTypes.string,
	onDelete: React.PropTypes.func,
	onAdd: React.PropTypes.func,
	};

ListInput.defaultProps = {
	blankText: '',
	cols: 1,
	onDelete: () => {},
	onAdd: () => {},
	};

module.exports = ListInput;
