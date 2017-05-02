/*
* core/static/core/react/core/components/RotatingIcon.jsx
* Quizzera
* Author: Rushy Panchal
* Description: Rotating icons.
*/

var React = require('react');

var Icon = require('core/components/Icon.jsx');

function RotatingIcon(props) {
	var newProps = new Object(props),
		rotating = props.rotating,
		className = props.className;

	if (rotating) className += ' rotating-icon';

	return <Icon {...newProps} className={className} />;
	}

RotatingIcon.propTypes = {
	rotating: React.PropTypes.bool,
	};

RotatingIcon.defaultProps = {
	rotating: false,
	className: '',
	};

module.exports = RotatingIcon;
