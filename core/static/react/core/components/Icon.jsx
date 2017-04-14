/*
* core/static/core/react/core/components/Icon.jsx
* Quizzera
* Author: Rushy Panchal
* Description: Ionicons icon.
*/

var React = require('react');

/*
* An Icon component is a wrapper around an icon. It shortens creating
* icons by appending the proper class prefixes.
*
* Required Props
* 	String i - icon name (without the 'ionicons ion-' prefix)
*
* Optional Props
* 	String size - font size to apply
*/
function Icon(props) {
	var iconName = props.i,
		fontSize = props.size,
		style = {},
		className = 'ionicons ion-' + iconName;
	if (fontSize) style.fontSize = fontSize;
	if (props.style) Object.assign(style, props.style);
	if (props.className) className += ' ' + props.className;

	return (<i {...props} className={className} style={style}></i>);
	}

Icon.propTypes = {
	i: React.PropTypes.string.isRequired,
	fontSize: React.PropTypes.string,
	};

module.exports = Icon;
