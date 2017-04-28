/*
* core/components/ExpandingTabs.jsx
* Author: Rushy Panchal
* Date: April 28th, 2017
*/

var React = require('react');

class ExpandingTabs extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			open: props.open,
			};

		this.tabClickHandler = this.tabClickHandler.bind(this);
		}

	componentWillReceiveProps(newProps) {
		if (this.state.open != newProps.open && newProps.open != -1)
			this.setState({open: newProps.open});
		}

	tabClickHandler(tabIndex) {
		var newTab = -1;
		if (tabIndex != this.state.open) newTab = tabIndex;
		this.setState({open: newTab});
		}

	render() {
		var tabWidth = 100 / this.props.tabs.length;

		var tabsDisplay = <div className='row'>
				{this.props.tabs.map((e, i) => {
					return <h2 className={'tab btn' + (i == this.state.open ? ' active' : '')}
						key={Math.random()} style={{width: `${tabWidth}%`}}
						onClick={() => this.tabClickHandler(i)}>
						{e.name}
					</h2>;
					})}
				</div>;

		if (this.props.tabs.length == 0) return <div></div>;

		if (this.state.open == -1) return tabsDisplay;
		else {
			return <div>
				{tabsDisplay}
				<div className='content'>
					{this.props.tabs[this.state.open].content}
				</div>
			</div>;
			}
		}
	}

ExpandingTabs.propTypes = {
	open: React.PropTypes.number,
	tabs: React.PropTypes.arrayOf(React.PropTypes.shape({
		name: React.PropTypes.string,
		content: React.PropTypes.element,
		})).isRequired,
	};

ExpandingTabs.defaultProps = {
	open: -1,
	}

module.exports = ExpandingTabs;
