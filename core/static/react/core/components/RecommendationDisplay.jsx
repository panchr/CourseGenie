/*
* core/components/RecommendationDisplay.jsx
* Author: Rushy Panchal
* Date: April 12th, 2017
* Description: Provides a list of rendered data.
*/

var React = require('react');

function RecommendationDisplay(props) {
	return <span className='suggestion-display'>
		<div className='11u'>
			<div>{props.short_name}</div>
			<div>{props.name}</div>
			<div>{props.reason}</div>
		</div>
	</span>;
	}

RecommendationDisplay.propTypes = {
	short_name: React.PropTypes.string.isRequired,
	name: React.PropTypes.string.isRequired,
	reason: React.PropTypes.string.isRequired,
	};

module.exports = RecommendationDisplay;
