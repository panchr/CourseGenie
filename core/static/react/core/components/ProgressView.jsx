/*
* core/components/ProgressView.jsx
* Author: Kathy Fan
* Date: April 28th, 2017
*/

var React = require('react');

var Icon = require('core/components/Icon.jsx'),
	ListView = require('core/components/ListView.jsx');

function ProgressView(props) {
	var p = props.progress;
	return <div>
		<ProgressItem data={p.degree} />
	</div>;
	}

function ProgressItem(props) {
	var data = props.data;
	if (data.length == 0) return null;

	var progress_type = data[0].requirement.parent_t[0].toUpperCase() + data[0].requirement.parent_t.slice(1);

	return <div>
		<h2>{progress_type}: {data[0].parent.name} ({data[0].parent.short_name})</h2>
		<ListView data={data} t={(e) => {
			var checkmark = null;
			if (e.completed)
				checkmark = <Icon i='ios-checkmark' style={{color: 'green'}} />
			else checkmark = <Icon i='ios-checkmark-outline' />;

			return <h3> {checkmark} {e.requirement.name}</h3>
			}} />
	</div>
	}

var reqType = React.PropTypes.shape({
	completed: React.PropTypes.boolean,
	requirement: React.PropTypes.shape({
		name: React.PropTypes.string,
		parent_t: React.PropTypes.string,
		}),
	parent: React.PropTypes.shape({
		name: React.PropTypes.string,
		short_name: React.PropTypes.string,
		}),
	});

ProgressView.propTypes = {
	progress: React.PropTypes.shape({
		degree: React.PropTypes.arrayOf(reqType),
		major: React.PropTypes.arrayOf(reqType),
		track: React.PropTypes.arrayOf(reqType),
		certificates: React.PropTypes.arrayOf(
			React.PropTypes.arrayOf(React.PropTypes.arrayOf(reqType),)),
		}).isRequired,
	};

module.exports = ProgressView;
