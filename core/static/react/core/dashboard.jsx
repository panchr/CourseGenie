/*
* core/dashboard.jsx
* Author: Rushy Panchal
* Date: April 9th, 2017
* Description: Render dashboard page.
*/

var React = require('react'),
	ReactDOM = require('react-dom');

import HTML5Backend from 'react-dnd-html5-backend';
import { DragDropContext } from 'react-dnd';
import { List, Map, fromJS } from 'immutable';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
  RecommendationDisplay = require('core/components/RecommendationDisplay.jsx'),
  SemesterDisplay = require('core/components/SemesterDisplay.jsx'),
	ListView = require('core/components/ListView.jsx'),
	GridView = require('core/components/GridView.jsx'),
	ErrorAlert = require('core/components/ErrorAlert.jsx'),
	Icon = require('core/components/Icon.jsx'),
	data = require('core/data.jsx');

function main() {
	var DashboardComp = DragDropContext(HTML5Backend)(Dashboard);
	ReactDOM.render(
		<DashboardComp calendar_ids={dashboard_data.user_calendars} />,
		document.getElementById('dashboard'));
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
		this.requests.push(data.calendar.getSemesters(this.props.calendar_ids[0],
			(data) => this.setState({semesters: fromJS(data)})));
		this.requests.push(data.recommendations.get(this.props.calendar_ids[0],
			(data) => this.setState({recommendations: new List(data)})));
		}

	dismissSuggestion(id, index) {
		this.requests.push(data.recommendations.dismiss(id));
		this.removeSuggestion(index);
		}

	removeSuggestion(index) {
		// NOTE: may need to refetch list of recommendations when this list is
		// nearly empty.
		this.setState({recommendations: this.state.recommendations.delete(index)});
		}

	addCourse(index, course) {
		var sems = this.state.semesters,
			current = sems.get(index);

		this.setState({
			semesters: sems.set(index,
				current.set('courses', current.get('courses').push(course))),
			});
		this.requests.push(data.calendar.addToSemester(current.get('id'), course,
			() => {}));
		}

	removeCourse(index, course_index, course) {
		var sems = this.state.semesters,
			current = sems.get(index);

		this.setState({
			semesters: sems.set(index,
				current.set('courses', current.get('courses').delete(course_index))),
			});
		this.requests.push(data.calendar.removeFromSemester(current.get('id'),
			course, () => {}));
		}

	componentWillUnmount() {
		this.requests.map((r) => r.abort());
		}

	render() {
		return (<div className="container">
				<ErrorAlert msg={this.state.errorMsg} />
				<div className="row">
					<div className="7u">
						<div style={{maxHeight: '80vh', overflowY: 'scroll'}}>
							<ListView t={(e, i) =>
								<SemesterDisplay {...e.toJS()} maxSize={6}
									onCourseAdd={(c) => this.addCourse(i, c)}
									onCourseRemove={(c, j) => this.removeCourse(i, j, c)} />
								} data={this.state.semesters} />
						</div>
					</div>
					<div className="5u">
						<h3>Recommendations</h3>
						<div style={{maxHeight: '80vh', overflowY: 'scroll'}}>
							<ListView t={(e, i) => {
								return <div className='recs'>
									<div className="row">
									<div className='10u'>
										<RecommendationDisplay {...e}
											onDragEnd={() => this.removeSuggestion(i)} />
									</div>
									<div className='2u'>
										<Icon i='ios-close-empty'
											className='btn large-icon' style={{color: 'LightSlateGray'}}
											onClick={() => this.dismissSuggestion(e.course_id, i)}
										/>
									</div>
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
