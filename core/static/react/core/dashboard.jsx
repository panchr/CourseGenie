/*
* core/dashboard.jsx
* Author: Rushy Panchal
* Date: April 9th, 2017
* Description: Render dashboard page.
*/

var React = require('react'),
	ReactDOM = require('react-dom');

import { List } from 'immutable';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
  RecommendationDisplay = require('core/components/RecommendationDisplay.jsx'),
	ListView = require('core/components/ListView.jsx'),
	GridView = require('core/components/GridView.jsx'),
	ErrorAlert = require('core/components/ErrorAlert.jsx'),
	Icon = require('core/components/Icon.jsx'),
	data = require('core/data.jsx');

function main() {
	ReactDOM.render(<Dashboard />, document.getElementById('dashboard'));
	}

class Dashboard extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			semesters: new List(),
			recommendations: new List(),
			errorMsg: '',
			};

		this.elems = {};
		this.requests = new Array();
		}

	componentWillMount() {
		data.installErrorHandler((msg) => this.setState({errorMsg: msg}));
		this.requests.push(data.schedule.getSemesters(
			(data) => this.setState({semesters: new List(data)})));
		this.requests.push(data.recommendations.get(
			(data) => this.setState({recommendations: new List(data)})));
		}

	dismissSuggestion(id, index) {
		this.requests.push(data.recommendations.dismiss(id));
		this.setState({recommendations: this.state.recommendations.delete(index)});
		}

	componentWillUnmount() {
		this.requests.map((r) => r.abort());
		}

	render() {
		return (<div className="container">
			<div className="container">
				<ErrorAlert msg={this.state.errorMsg} />
				<div className="row">
					<div className="7u">
						<h1>Schedule</h1>
						<ListView t={(e) => {
							return <div>
								<h2>{e.name}</h2>
								<GridView t={(c) => {
									return <CourseDisplay {...c} extended={true} />;
									}} rows={2} cols={3} data={e.courses}
									blankElement={() =>
										<Icon i='ios-plus' className='large-icon'
										style={{color: 'green'}} />} />
							</div>;
							}} data={this.state.semesters}/>
					</div>
					<div className="5u">
						<h1>Recommendations</h1>
						<ListView t={(e, i) => {
							return <div className="row">
								<div className='9u'><RecommendationDisplay {...e} /></div>
								<div className='3u'>
									<Icon i='ios-close-outline'
										className='btn large-icon' style={{color: 'red'}}
										onClick={() => this.dismissSuggestion(e.course_id, i)}
									/>
								</div>
							</div>;
							}} data={this.state.recommendations} />
					</div>
				</div>
			</div>
		</div>);
		}
	}

jQuery(document).ready(main);
