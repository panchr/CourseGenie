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
		<ProgressItem data={p.degree}
			onProgressChange={(i, id) => props.onProgressChange('degree', null, i, id)} />
		<ProgressItem data={p.major}
			onProgressChange={(i, id) => props.onProgressChange('major', null, i, id)}/>
		<ProgressItem data={p.track}
			onProgressChange={(i, id) => props.onProgressChange('track', null, i, id)} />
		<ListView data={p.certificates} t={(e, j) => 
			<ProgressItem data={e}
				onProgressChange={(i, id) =>
					props.onProgressChange('certificates', j, i, id)}/>}
		/>
	</div>;
	}

var reqType = React.PropTypes.shape({
	completed: React.PropTypes.boolean,
	user_completed: React.PropTypes.boolean,
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
			React.PropTypes.arrayOf(reqType)),
		}).isRequired,
	onProgressChange: React.PropTypes.func,
	};

ProgressView.defaultProps = {
	onProgressChange: () => {},
	};

function ProgressItem(props) {
	var data = props.data;
	if (data.length == 0) return <div style={{display: 'hidden'}}></div>;

	var progress_type = data[0].requirement.parent_t[0].toUpperCase() + data[0].requirement.parent_t.slice(1),
		parent = data[0].parent;

	return <div>
		<h2>{progress_type}: {parent.name}
			{parent.short_name ? ` (${parent.short_name})`: ''}</h2>
		<ListView data={data} t={(e, i) => {
			var checkmark = null;
			if (e.completed || e.user_completed)
				checkmark = <Icon i='ios-checkmark' className='btn icon-hover success'
					onClick={() => props.onProgressChange(i, e.id)} />
			else
				checkmark = <Icon i='ios-checkmark-outline' className='btn icon-hover'
					onClick={() => props.onProgressChange(i, e.id)} />

			return <h3>{checkmark} {e.requirement.name}</h3>
			}} />
	</div>
	}

module.exports = ProgressView;
