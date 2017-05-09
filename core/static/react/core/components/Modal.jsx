/*
* core/components/Modal.jsx
* Author: Rushy Panchal
* Date: April 25th, 2017
* Description: Provides a modal-type interface.
*/

var React = require('react');

var Icon = require('core/components/Icon.jsx');

class Modal extends React.Component {
	constructor(props) {
		super(props);
		this.mainElement = null;
		}

	componentDidUpdate() {
		if (this.mainElement != null && this.props.open) {
			this.mainElement.focus();
			}
		}

	render() {
		this.mainElement = null;
		var className = 'modal fixed-center';
		if (this.props.className) className += ' ' + this.props.className;

		const btn = <div className='center-parent' style={{width: '50%'}}>
					<a className="button fit btn" onClick={this.props.onButtonClick}>{this.props.buttonText}</a>
				</div>;

		if (this.props.open) {
			return <div className={className} tabIndex=""
				//onBlur={this.props.onClose}
				ref={(e) => this.mainElement = e}>
				<Icon i='ios-close-empty'
					className='btn large-icon' style={{color: 'LightSlateGray', float: 'right'}}
					onClick={this.props.onClose} />
				<br/>
				{this.props.children}
				<br/>
				{this.props.button? btn: null}
			</div>;
			}
		else return <div style={{display: 'none'}}></div>;
		}
	}

Modal.propTypes = {
	open: React.PropTypes.bool,
	button: React.PropTypes.bool,
	buttonText: React.PropTypes.string,
	onClose: React.PropTypes.func,
	onButtonClick: React.PropTypes.func,
	};

Modal.defaultProps = {
	open: false,
	button: true,
	buttonText: 'Close',
	onClose: () => {},
	onButtonClick: () => {},
	};

module.exports = Modal;
