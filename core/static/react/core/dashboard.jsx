/*
* core/dashboard.jsx
* Author: Rushy Panchal
* Date: April 9th, 2017
* Description: Render dashboard page.
*/

var React = require('react'),
	ReactDOM = require('react-dom'),
	jQuery = require('jquery');

import HTML5Backend from 'react-dnd-html5-backend';
import { DragDropContext } from 'react-dnd';
import { List, Map, fromJS } from 'immutable';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
  RecommendationDisplay = require('core/components/RecommendationDisplay.jsx'),
  SemesterDisplay = require('core/components/SemesterDisplay.jsx'),
	ListView = require('core/components/ListView.jsx'),
	GridView = require('core/components/GridView.jsx'),
	ListInput = require('core/components/ListInput.jsx'),
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
	
	// null value so it doesn't crash on initial load
	var tracksByMajor = {};
	tracksByMajor[null] = new Array();
	for (var i=0; i < dashboard_data.majors.length; i++) {
		tracksByMajor[dashboard_data.majors[i].id] = new Array();
		}

	for (var i=0; i < dashboard_data.tracks.length; i++) {
		var t = dashboard_data.tracks[i];
		tracksByMajor[t.major_id].push(t);
		}

	ReactDOM.render(
		<DashboardComp
			calendars={dashboard_data.user_calendars}
			majors={dashboard_data.majors} tracks={tracksByMajor}
			certificates={dashboard_data.certificates}
			minRecommendations={10}
			defaultCalendar={dashboard_data.user_calendars[0].id}
			/>,
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
			progress: new Map({
				degree: new List(),
				major: new List(),
				track: new List(),
				certificates: new List(),
				}),
			currentCalendar: props.defaultCalendar,
			calendarSettingsModalOpen: false,
			currentMajor: null,
			currentTrack: null,
			currentCertificates: new List(),
			};

		this.elems = {};
		this.nonstateData = {};
		this.requests = new Array();
		this.progressChange = this.progressChange.bind(this);
		this.setCalendar = this.setCalendar.bind(this);

		this._cached_data = {};
		}

	componentWillMount() {
		data.installErrorHandler((msg) => this.setState({errorMsg: msg}));
		this.loadAllData();
		}

	componentWillUnmount() {
		this.requests.map((r) => r.abort());
		}

	setCalendar(calendar_id) {
		// deep clone: cache current state before switching to avoid refetching.
		this._cached_data[this.state.currentCalendar] = jQuery.extend(true, {}, this.state);
		this.setState({currentCalendar: calendar_id}, () => {
			if (calendar_id in this._cached_data) {
				this.setState(this._cached_data[calendar_id]);
				}
			else this.loadAllData();
			});
		}

	loadAllData() {
		this.requests.push(data.calendar.getData(this.state.currentCalendar,
			(data) => {
				var data = fromJS(data);
				this.setState({semesters: data.get('semesters'),
					sandbox: data.get('sandbox'), currentMajor: data.get('major'),
					currentTrack: data.get('track'),
					currentCertificates: data.get('certificates'),
					}, () => this.loadRecommendations(() => this.loadProgress()));
			}));
		}

	loadRecommendations(callback=() => null) {
		this.requests.push(data.recommendations.get(this.state.currentCalendar,
			(data) => {
				this.setState({recommendations: new List(data)});
				callback();
			}));
		}

	loadProgress() {
		this.requests.push(data.calendar.getProgress(this.state.currentCalendar,
			(data) => {
				var progressData = {
					degree: new Array(),
					major: new Array(),
					track: new Array(),
					certificates: new Object(),
					};

				var currentCertificateIds = this.state.currentCertificates.map(
					(x) => x.get('id'));

				for (var i=0; i < data.length; i++) {
					var p = data[i],
						parent_type = p.requirement.parent_t;

					// Filter out irrelevant progresses (i.e. ones left over from
					// user marking them complete manually).
					if ((parent_type == 'major' && p.parent.id != this.state.currentMajor)
						|| (parent_type == 'track' && p.parent.id != this.state.currentTrack)
						|| (parent_type == 'certificate' && currentCertificateIds.indexOf(p.parent.id) == -1)) continue;

					if (parent_type == 'certificate') {
						if (progressData.certificates[p.parent.id] == undefined)
							progressData.certificates[p.parent.id] = new Array();
						progressData.certificates[p.parent.id].push(p);
						}
					else progressData[p.requirement.parent_t].push(p);
					}

				// Bubble incomplete requirements to top
				function bubbleIncomplete(rs) {
					return rs.filter((x) => ! (x.completed || x.user_completed))
						.concat(rs.filter(x => x.completed || x.user_completed));
					}

				progressData.degree = bubbleIncomplete(progressData.degree);
				progressData.major = bubbleIncomplete(progressData.major);
				progressData.track = bubbleIncomplete(progressData.track);

				progressData.certificates = Object.keys(progressData.certificates).sort().map(
					(i) => bubbleIncomplete(progressData.certificates[i]));

				this.setState({progress: fromJS(progressData)});
				}));
		}

	addMessage(m) {
		this.setState({messages: this.state.messages.push(m)});
		}

	dismissSuggestion(id, index) {
		this.requests.push(data.recommendations.dismiss(id));
		this.removeSuggestion(index);
		}

	removeSuggestion(index) {
		var newRecs = this.state.recommendations.delete(index);
		this.setState({recommendations: newRecs});
		if (newRecs.size < this.props.minRecommendations) {
			this.loadRecommendations();
			}
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
		this.requests.push(data.calendar.addToSandbox(this.state.currentCalendar,
			course, () => {
			this.setState({sandbox: this.state.sandbox.push(course)});
			}));
		}

	removeFromSandbox(i, course) {
		this.setState({sandbox: this.state.sandbox.remove(i)});
		this.requests.push(data.calendar.removeFromSandbox(
			this.state.currentCalendar, course));
		}

	progressChange(t, innerIndex, index, id) {
		var toUpdate = this.state.progress.get(t);

		if (t == 'certificates') toUpdate = toUpdate.get(innerIndex);

		var p = toUpdate.get(index),
			new_completed = ! (p.get('user_completed') || p.get('completed'));

		var updated = null;
		if (new_completed)
			updated = toUpdate.delete(index).push(p.set('user_completed', true));
		else
			updated = toUpdate.delete(index).insert(0,
				p.set('user_completed', false).set('completed', false));

		var fullUpdated = null;
		if (t == 'certificates') fullUpdated = this.state.progress.set(t, this.state.progress.get(t).set(innerIndex, updated));
		else fullUpdated = this.state.progress.set(t, updated);

		var patch_data = {user_completed: new_completed};
		if (! new_completed) patch_data.completed = false;

		this.setState({progress: fullUpdated});
		this.requests.push(data.calendar.setSingleProgress(id, patch_data));
		}

	saveCalendarSettings() {
		var update_data = {
			major: this.elems.major_input.value,
			track: this.elems.track_input.value == 'null' ? null: this.elems.track_input.value,
			};

		// Remove track if not found in the current major.
		var trackInMajor = false;
		for (var i=0; i < this.props.tracks[update_data.major].length; i++) {
			var t = this.props.tracks[update_data.major][i];
			if (t.id == update_data.track) {
				trackInMajor = true;
				break;
				}
			}

		if (! trackInMajor) update_data.track = null;

		// var shouldReload = (update_data.track != this.state.currentTrack ||
		// 	update_data.major != this.nonstateData.old_major);

		this.requests.push(data.calendar.saveSettings(this.state.currentCalendar,
			update_data, () => this.loadAllData()));

		this.setState({
			calendarSettingsModalOpen: false,
			currentMajor: update_data.major,
			currentTrack: update_data.track,
			});
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

				<Modal open={this.state.calendarSettingsModalOpen} buttonText='Save'
					onButtonClick={() => this.saveCalendarSettings()}
					onClose={() => this.setState({calendarSettingsModalOpen: false})}>
					<div className="row">
						<h1>Concentration Settings</h1>
					</div>
					<div className="row">
						<div className="12u"><h2>Major</h2></div>
						<div className="12u">
						<select name="selected-major" value={this.state.currentMajor}
								ref={(e) => this.elems.major_input = e}
								onChange={(e) => {
									this.nonstateData.old_major = this.state.currentMajor;
									this.setState({currentMajor: e.target.value});
									}}>
								{this.props.majors.map((e) =>
									<option value={e.id} key={Math.random()}>
										{e.name}
									</option>)}
							</select>
						</div>
					</div>
					<div className="row">
						<div className="12u"><h2>Track</h2></div>
						<div className="12u">
							<select name="selected-track" defaultValue={this.state.currentTrack}
								ref={(e) => this.elems.track_input = e}>
								<option value="null">None</option>
								{this.props.tracks[this.state.currentMajor].map((e) =>
									<option value={e.id} key={Math.random()}>{e.name}</option>)}
							</select>
						</div>
					</div>
					<div className="row">
						<div className="12u"><h2>Certificate(s)</h2></div>
						<div className="12u">
						<ListInput t={(e) => <span>{e.name}</span>}
							data={this.state.currentCertificates.toJS()}
							blankText='None yet!'
							getInput={() => this.props.certificates[this.elems.certificate_input.value]} cols={2}
							onAdd={(e) => {
								data.calendar.addCertificate(this.state.currentCalendar, e.id);
								}}
							onDelete={(e, i) => {
								data.calendar.removeCertificate(this.state.
								currentCalendar, e.id)
								}}>
								<select name="selected-certificate"
									ref={(e) => this.elems.certificate_input = e}>
									{this.props.certificates.map((e, i) =>
										<option value={i} key={Math.random()}>
											{e.name}
										</option>)}
								</select>
						</ListInput>
						</div>
					</div>
				</Modal>

				<div className='messages-list'>
					<MessageList messages={this.state.messages.toJS()}
						onDismiss={(i) => this.setState({messages: this.state.messages.delete(i)})} />
				</div>

				<div className="row">
					{this.props.calendars.map((e) => {
						return <h1 onClick={() => this.setCalendar(e.id)}>{e.name}</h1>;
						})}
				</div>

				<div className="row">
					<div className='7u hovering-tabs'>
						<ExpandingTabs tabs={[
							{name: 'Sandbox', content:
								<Sandbox onCourseAdd={(c) => this.addToSandbox(c)}
									onCourseRemove={(c, i) => this.removeFromSandbox(i, c)}
									courses={this.state.sandbox.toJS()} />},
							{name: 'Progress', content: 
								<div className='row'>
								<div className="12u">
									<button className='button-add btn force-center'
										onClick={() => this.setState({calendarSettingsModalOpen: true})}
										style={{marginTop: '1em'}}>
											Concentration Settings
										</button>
								</div>
								<div className="12u">
									<ProgressView progress={this.state.progress.toJS()}
									onProgressChange={this.progressChange} />
								</div>
								</div>},
							]} />
					</div>

					<div className="7u">
						<div className='scrollable-container no-horizontal-scroll'>
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
					<div className="5u" id="float">
						<h3>Recommendations</h3>
						<div className='scrollable-container no-horizontal-scroll'>
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
