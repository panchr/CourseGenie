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
	MessageList = require('core/components/MessageList.jsx'),
	ErrorAlert = require('core/components/ErrorAlert.jsx'),
	Icon = require('core/components/Icon.jsx'),
	Modal = require('core/components/Modal.jsx'),
	ExpandingTabs = require('core/components/ExpandingTabs.jsx'),
	Sandbox = require('core/components/Sandbox.jsx'),
	ProgressView = require('core/components/ProgressView.jsx'),
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
			messages: new List(),
			courseInputModalOpen: false,
			selectedSemester: new Object(),
			selectedSemester_index: null,
			sandbox: new List(),
			progress: new Map(),
			};

		this.elems = {};
		this.requests = new Array();
		}

	componentWillMount() {
		data.installErrorHandler((msg) => this.setState({errorMsg: msg}));
		this.requests.push(data.calendar.getData(this.props.calendar_ids[0],
			(data) => {
				var data = fromJS(data);
				this.setState({semesters: data.get('semesters'),
					sandbox: data.get('sandbox')});
			}));
		this.requests.push(data.calendar.getProgress(this.props.calendar_ids[0],
			(data) => {
				var progressData = {
					degree: new Array(),
					major: new Array(),
					track: new Array(),
					certificates: new Object(),
					};

				// Group progress data into degree/major/track/certificates.
				for (var i=0; i < data.length; i++) {
					var p = data[i],
						parent_type = p.requirement.parent_t;
					if (parent_type == 'certifcate') {
						if (progressData.certificates[p.parent.id] == undefined)
							progressData.certificates[p.parent.id] = new Array();
						progressData.certificates[p.parent.id].push(p);
						}
					else progressData[p.requirement.parent_t].push(p);
					}

				// Bubble incomplete requirements to top
				function bubbleIncomplete(rs) {
					return rs.filter((x) => ! x.completed).concat(rs.filter(x => x.completed));
					}

				progressData.degree = bubbleIncomplete(progressData.degree);
				progressData.major = bubbleIncomplete(progressData.major);
				progressData.track = bubbleIncomplete(progressData.track);

				progressData.certificates = Object.keys(progressData.certificates).sort().map(
					(i) => bubbleIncomplete(progressData.certificates[i]));

				this.setState({progress: fromJS(progressData)});
				}));
		this.requests.push(data.recommendations.get(this.props.calendar_ids[0],
			(data) => this.setState({recommendations: new List(data)})));
		}

	componentWillUnmount() {
		this.requests.map((r) => r.abort());
		}

	addMessage(m) {
		this.setState({messages: this.state.messages.push(m)});
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
		var current = this.state.semesters.get(index);

		this.requests.push(data.calendar.addToSemester(current.get('id'), course,
			() => {this.addCourseToDisplay(index, course)}));
		}

	addCourseToDisplay(index, course) {
		var sems = this.state.semesters,
			current = sems.get(index);

		this.setState({
			semesters: sems.set(index,
				current.set('courses', current.get('courses').push(course))),
			recommendations: this.state.recommendations.filter((r) => r.course.course_id != course.course_id)
			});
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

	addDirectCourse(semester_index) {
		var department = this.elems.department_input.value,
			number = this.elems.number_input.value,
			c = (department + " " + number).toUpperCase(),
			current = this.state.semesters.get(semester_index);

		if (department == '' || number == '') {
			this.addMessage({message: 'Cannot input a blank course.', t: 'error'});
			}
		else if (! /^\w{3}$/.test(department)) {
			this.addMessage({message: 'The department must be 3 letters.', t: 'error'});
			}
		else if (! /^\d{3}[a-zA-Z]?$/.test(number)) {
			this.addMessage({message: 'The course number must be a number, optionally followed by a letter.', t: 'error'});
			}
		else {
			this.requests.push(data.calendar.addToSemesterByCourseName(current.get('id'), c, (course_data) => {
				this.addCourseToDisplay(semester_index, course_data);
				}));
			}
		}

	addToSandbox(course) {
		this.requests.push(data.calendar.addToSandbox(this.props.calendar_ids[0],
			course, () => {
			this.setState({sandbox: this.state.sandbox.push(course)});
			}));
		}

	removeFromSandbox(i, course) {
		this.setState({sandbox: this.state.sandbox.remove(i)});
		this.requests.push(data.calendar.removeFromSandbox(
			this.props.calendar_ids[0], course));
		}

	render() {
		return (<div className="container">
				<ErrorAlert msg={this.state.errorMsg} />
				<Modal open={this.state.courseInputModalOpen} buttonText='Add'
					onButtonClick={() => {
						this.addDirectCourse(this.state.selectedSemester_index);
						this.setState({courseInputModalOpen: false, selectedSemester: {}});
						}}
					onClose={() => this.setState({courseInputModalOpen: false, selectedSemester: {},
						selectedSemester_index: null})}>
					<h1>{this.state.selectedSemester.term_display} {this.state.selectedSemester.year}</h1>
					<div className='row'>
						<div className='6u'>
							<span>Department</span>
						</div>
						<div className='6u'>
							<span>Number</span>
						</div>
					</div>
					<div className='row no-children-top-padding'>
						<div className="6u">
							<input placeholder="e.g. COS" type="text" className="text"
							ref={(e) => this.elems.department_input = e} />
						</div>
						<div className="6u$">
							<input placeholder="e.g. 333" type="text" className="text"
						 	ref={(e) => this.elems.number_input = e} />
							{/* refs are required (as callbacks) to get input */}
						</div>
					</div>
				</Modal>
				<div className='messages-list'>
					<MessageList messages={this.state.messages.toJS()}
						onDismiss={(i) => this.setState({messages: this.state.messages.delete(i)})} />
				</div>

				<div className="row">
					<div className='7u hovering-tabs'>
						<ExpandingTabs tabs={[
							{name: 'Sandbox', content:
								<Sandbox onCourseAdd={(c) => this.addToSandbox(c)}
									onCourseRemove={(c, i) => this.removeFromSandbox(i, c)}
									courses={this.state.sandbox.toJS()} />},
							{name: 'Progress', content: 
								<ProgressView progress={this.state.progress.toJS()} />},
							]} />
					</div>

					<div className="7u">
						<div style={{maxHeight: '80vh', overflowY: 'scroll'}}>
							<ListView t={(e, i) =>
								<SemesterDisplay {...e.toJS()} maxSize={6}
									onError={(err) => this.setState({messages: this.state.messages.push(err)})}
									onCourseAdd={(c) => this.addCourse(i, c)}
									onCourseRemove={(c, j) => this.removeCourse(i, j, c)}
									onPlusClick={() => {
										if (! this.state.courseInputModalOpen)
											this.setState({courseInputModalOpen: true, selectedSemester: e.toJS(),
												selectedSemester_index: i});
										}} />
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
											onClick={() => this.dismissSuggestion(e.course.course_id, i)}
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
