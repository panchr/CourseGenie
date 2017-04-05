
var React = require('react');

class CourseDisplay extends React.Component {
	/*
	* Required Props
	* 	String department
	* 	String number
	*/
	constructor(props) {
		super(props);
		}

	render() {
		return (<span>{this.props.department} {this.props.number}</span>);
		}
	}

CourseDisplay.propTypes = {
	department: React.PropTypes.string.isRequired,
	number: React.PropTypes.string.isRequired,
	}

module.exports = CourseDisplay;
