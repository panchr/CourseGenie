/*
* core/dashboard.jsx
* Author: Rushy Panchal
* Date: April 9th, 2017
* Description: Render dashboard page.
*/

const React = require('react'),
	ReactDOM = require('react-dom'),
	jQuery = require('jquery'),
	classNames = require('classnames');

// var Dropdown = require('react-simple-dropdown');

import Dropdown, { DropdownTrigger, DropdownContent } from 'react-simple-dropdown';
import HTML5Backend from 'react-dnd-html5-backend';
import { DragDropContext } from 'react-dnd';
import { List, Map, fromJS } from 'immutable';
import Cookies from 'universal-cookie';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
  RecommendationDisplay = require('core/components/RecommendationDisplay.jsx'),
  SemesterDisplay = require('core/components/SemesterDisplay.jsx'),
	ListView = require('core/components/ListView.jsx'),
	GridView = require('core/components/GridView.jsx'),
	ListInput = require('core/components/ListInput.jsx'),
	MessageList = require('core/components/MessageList.jsx'),
	ErrorAlert = require('core/components/ErrorAlert.jsx'),
	Icon = require('core/components/Icon.jsx'),
	RotatingIcon = require('core/components/RotatingIcon.jsx'),
	Modal = require('core/components/Modal.jsx'),
	ExpandingTabs = require('core/components/ExpandingTabs.jsx'),
	Sandbox = require('core/components/Sandbox.jsx'),
	ProgressView = require('core/components/ProgressView.jsx'),
	CalendarSettings = require('core/components/CalendarSettings.jsx'),
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
			defaultCalendar={0}
			majors={dashboard_data.majors}
			tracks={tracksByMajor}
			certificates={dashboard_data.certificates}
			profile={dashboard_data.profile_id}
			minRecommendations={10}
			/>,
		document.getElementById('dashboard'));
	}

class Dashboard extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			semesters: new List(),
			recommendations: new List(),
			messages: new List(),
			selectedSemester: new Object(),
			selectedSemester_index: null,
			selectedSandbox: false,
			sandbox: new List(),
			progress: new Map({
				degree: new List(),
				major: new List(),
				track: new List(),
				certificates: new List(),
				}),
			calendars: fromJS(props.calendars),
			calendarSettingsModalOpen: false,
			courseInputModalOpen: false,
			calendarAddModalOpen: false,
			confirmationModalOpen: false,
			toDeleteCalendar: null,
			currentCalendar: props.defaultCalendar,
			currentMajor: null,
			currentTrack: null,
			currentCertificates: new List(),
			loadingData: false,
			refreshQueued: false,
			};

		this.elems = {};
		this.requests = new Array();
		this.intervals = new Array();
		this.progressChange = this.progressChange.bind(this);
		this.setCalendar = this.setCalendar.bind(this);

		this._cached_calendars = {};
		}

	componentWillMount() {
		data.installErrorHandler((msg) => this.addMessage({message: msg, t: 'error'}));
		this.loadAllData();

		const cookies = new Cookies();
		if (! Boolean(cookies.get('help-displayed'))) {
			cookies.set('help-displayed', true);
			this.addMessage({
				message: 'Drag courses from your recommendations into a semester or your Sandbox tab. View & Edit your progress through the Progress tab.',
				header: 'Welcome!',
				t: 'success',
				});
			}

		// Background refresh data every 5s if needed.
		this.intervals.push(setInterval(() => {
			if (this.state.refreshQueued && ! this.state.loadingData) {
				this.loadAllData();
				this.setState({refreshQueued: false});
				}
			}, 5000));
		}

	componentWillUnmount() {
		this.requests.map((r) => r.abort());
		this.intervals.map((i) => clearInterval(i));
		}

	calendarId(index) {
		if (index == null || index == undefined) index = this.state.currentCalendar;
		return this.state.calendars.get(index).get('id');
		}

	setCalendar(index, cache=true) {
		// deep clone: cache current state before switching to avoid refetching.
		const old_cal_id = this.calendarId();

		if (cache) {
			var cached_data = jQuery.extend(true, {}, this.state);
			delete cached_data.calendars;
			delete cached_data.currentCalendar;
			this._cached_calendars[old_cal_id] = cached_data;
			}
		this.setState({currentCalendar: index}, () => {
			let calendar_id = this.calendarId(index);
			if (calendar_id in this._cached_calendars && cache) {
				this.setState(this._cached_calendars[calendar_id]);
				}
			else this.loadAllData();
			});
		}

	loadAllData() {
		this.setState({loading: true});
		this.requests.push(data.calendar.getData(this.calendarId(),
			(data) => {
				var data = fromJS(data);
				this.setState({semesters: data.get('semesters'),
					sandbox: data.get('sandbox'),
					currentMajor: data.get('major'),
					currentTrack: data.get('track'),
					currentCertificates: data.get('certificates'),
					}, () => this.loadRecommendations(() => {
						this.loadProgress();
						this.setState({loading: false});
						}));
			}));
		}

	loadRecommendations(callback=() => null) {
		this.requests.push(data.recommendations.get(this.calendarId(),
			(data) => {
				this.setState({recommendations: new List(data)});
				callback();
			}));
		}

	loadProgress() {
		this.requests.push(data.calendar.getProgress(this.calendarId(),
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
		this.requests.push(data.recommendations.dismiss(id,
			() => this.setState({refreshQueued: true})));
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
			() => this.addCourseToDisplay(index, course)));
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
			course, () => this.setState({refreshQueued: true})));
		}

	addDirectCourse(semester_index) {
		const department = this.elems.department_input.value,
			number = this.elems.number_input.value,
			c = (department + " " + number).toUpperCase(),
			sandbox = semester_index == null && this.state.selectedSandbox;

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
			if (sandbox) {
				this.requests.push(data.calendar.addToSandboxShort(this.calendarId(), c,
					(course_data) => this.setState({sandbox: this.state.sandbox.push(course_data), refreshQueued: true})))
				}
			else {
				const current = this.state.semesters.get(semester_index);
				this.requests.push(data.calendar.addToSemesterByCourseName(current.get('id'), c, (course_data) => {
					this.addCourseToDisplay(semester_index, course_data);
					this.setState({refreshQueued: true});
					}));
				}
			}
		}

	addToSandbox(course) {
		this.requests.push(data.calendar.addToSandbox(this.calendarId(),
			course, () => {
			this.setState({sandbox: this.state.sandbox.push(course)});
			}));
		}

	removeFromSandbox(i, course) {
		this.setState({sandbox: this.state.sandbox.remove(i)});
		this.requests.push(data.calendar.removeFromSandbox(
			this.calendarId(), course, () => this.setState({refreshQueued: true})));
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
		this.requests.push(data.calendar.setSingleProgress(id, patch_data,
			() => this.setState({refreshQueued: true})));
		}

	saveCalendarSettings(update_data) {
		this.requests.push(data.calendar.saveSettings(this.calendarId(),
			update_data, () => this.loadAllData()));

		this.setState({
			calendarSettingsModalOpen: false,
			currentMajor: Number(update_data.major),
			currentTrack: Number(update_data.track),
			calendars: this.state.calendars.set(this.state.currentCalendar,
				this.state.calendars.get(this.state.currentCalendar)
					.set('name', update_data.name))
			});
		}

	addNewCalendar(post_data) {
		post_data.degree = 1;
		post_data.profile_id = this.props.profile;

		this.requests.push(data.calendar.create(post_data, (cal) => {
			this.setState({calendars: this.state.calendars.insert(0, new Map(cal))},
				() => this.setCalendar(0, false));
			// avoid caching data here because of race condition
			}));
		}

	deleteCalendar() {
		const index = this.state.toDeleteCalendar;
		if (index == null) return;

		const id = this.state.calendars.get(index).get('id');

		this.setState({
			calendars: this.state.calendars.delete(index),
			toDeleteCalendar: null,
			confirmationModalOpen: false,
			});
		if (index == this.state.currentCalendar) this.setCalendar(0, false);

		this.requests.push(data.calendar.delete(id));
		}

	render() {
		const currentCertificateIds = this.state.currentCertificates.map((x) => x.get('id'));

		return (<div className="container">
				<div className="row">
					<div className="5u">
						<Dropdown>
							<DropdownTrigger className='btn'>Calendars <Icon i='ios-arrow-down' /></DropdownTrigger>
							<DropdownContent>
								<h2 className='dropdown-item btn' style={{fontSize: '100%', color: 'green'}}
									onClick={() => this.setState({calendarAddModalOpen: true})}>
									New Calendar &nbsp; <Icon i='ios-plus-empty'
										style={{color: 'green'}} />
								</h2>
								<ul className="no-margin">
								{this.state.calendars.map((e, i) => {
									return <li key={Math.random()} className='btn dropdown-item'>
										<h2 style={{fontSize: '100%', textAlign: 'left'}}>
											<span onClick={() => this.setCalendar(i)}
												className={classNames({'active-calendar': i == this.state.currentCalendar})}>
											{e.get('name')} &nbsp;
											</span>
											{this.state.calendars.size == 1? null:
												// can't delete last calendar
												<span onClick={() => this.setState({confirmationModalOpen: true, toDeleteCalendar: i})}>
												<Icon i='ios-close-empty' style={{color: 'LightSlateGray'}} />
													</span>}
										</h2>
									</li>;
								})}
								</ul>
							</DropdownContent>
						</Dropdown>
					</div>
					<div className="2u hidemobile">
						<button className='cal-button btn'
							onClick={() => this.setState({calendarSettingsModalOpen: true})}>
								Calendar Settings
							</button>
						</div>
						<br/>
				</div>

				<div className="row">
					<div className='7u hovering-tabs small-left-padding'>
						<ExpandingTabs tabs={[
							{name: 'Sandbox', content:
								<Sandbox onCourseAdd={(c) => this.addToSandbox(c)}
									onCourseRemove={(c, i) => this.removeFromSandbox(i, c)}
									onPlusClick={() => {
										if (! this.state.courseInputModalOpen)
											this.setState({
												courseInputModalOpen: true,
												selectedSandbox: true,
												selectedSemester: {}, selectedSemester_index: null,
												});
										}}
									courses={this.state.sandbox.toJS()} />},
							{name: 'Progress', content:
								<div className='row small-left-padding'>
									<div className="12u">
										<ProgressView progress={this.state.progress.toJS()}
										onProgressChange={this.progressChange} />
									<br/>
									</div>
								</div>},
							]} />
					</div>

					<div className="7u no-padding">
						<div className="grid-pad scrollable-container no-horizontal-scroll">
							<ListView t={(e, i) =>
								<SemesterDisplay {...e.toJS()} maxSize={6}
									onError={(err) => this.setState({messages: this.state.messages.push(err)})}
									onCourseAdd={(c) => this.addCourse(i, c)}
									onCourseRemove={(c, j) => this.removeCourse(i, j, c)}
									onPlusClick={() => {
										if (! this.state.courseInputModalOpen)
											this.setState({
												courseInputModalOpen: true, selectedSemester: e.toJS(),
												selectedSemester_index: i});
										}} />
								} data={this.state.semesters} />
						</div>
					</div>
					<div className="5u move-up hidemobile" id="float">
						<h3>
							Recommendations &nbsp;
							<span className='tooltip-bottom' data-tooltip='Drag recommendations into your calendar from here.'>
							<Icon i='ios-help-outline' />
							</span>

							<RotatingIcon rotating={this.state.loading}
									i='ios-loop-strong' onClick={() => this.loadAllData()}
									style={{float: 'right', color: '#009688'}} className='btn' />
						</h3>
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

			{/* Hovering/Positioned Content */}
				<Modal open={this.state.courseInputModalOpen} buttonText='Add'
					onButtonClick={() => {
						this.addDirectCourse(this.state.selectedSemester_index);
						this.setState({courseInputModalOpen: false, selectedSandbox: false,
							selectedSemester: {}, selectedSemester_index: null});
						}}
					onClose={() => this.setState({courseInputModalOpen: false, selectedSemester: {}, selectedSemester_index: null
						})}>
					{this.state.selectedSandbox ?
							<h1 style={{fontSize: '1.2em', paddingLeft: '0'}}>Sandbox</h1>
							:
							<h1 style={{fontSize: '1.2em', paddingLeft: '0'}}>{this.state.selectedSemester.term_display} {this.state.selectedSemester.year}</h1>
					}
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

				<Modal open={this.state.confirmationModalOpen} button={false}
					onClose={() => this.setState({confirmationModalOpen: false})}>
					<h2>Do you really want to delete this calendar?</h2>
					<h3 className='center topbtm'>{this.state.toDeleteCalendar != null ? this.state.calendars.get(this.state.toDeleteCalendar).get('name'): null}</h3>
					<div className='row'>
						<div className="6u">
							<span className="button-delete btn"
								onClick={() => this.deleteCalendar()}>
								Delete</span>
						</div>
						<div className="6u" style={{paddingLeft: '3em'}}>
							<span className="button-add btn"
								onClick={() => this.setState({confirmationModalOpen: false})}>
								Cancel</span>
						</div>
					</div>
				</Modal>

				<CalendarSettings addMode open={this.state.calendarAddModalOpen}
					onSave={(data) => {
						this.addNewCalendar(data);
						this.setState({calendarAddModalOpen: false});
						}}
					onClose={() => this.setState({calendarAddModalOpen: false})}
					header='Add Calendar' majors={this.props.majors}
					tracks={this.props.tracks} certificates={this.props.certificates}
					currentMajor={this.state.currentMajor}
					currentTrack={this.state.currentTrack}
					currentCertificates={this.state.currentCertificates.toJS()}
					/>

				<CalendarSettings open={this.state.calendarSettingsModalOpen}
					onSave={(data) => {
						this.saveCalendarSettings(data);
						this.setState({calendarSettingsModalOpen: false});
						}}
					onClose={() => this.setState({calendarSettingsModalOpen: false})}
					onCertificateAdd={(e) => {
						data.calendar.addCertificate(this.calendarId(), e.id,
							() => this.setState({refreshQueued: true}));
						this.setState({currentCertificates: this.state.currentCertificates.push(new Map(e))});
						}}
					onCertificateRemove={(e, i) => {
						data.calendar.removeCertificate(this.calendarId(), e.id, () => this.setState({refreshQueued: true}));
						this.setState({currentCertificates: this.state.currentCertificates.remove(i)});
						}}
					header='Edit Calendar' majors={this.props.majors}
					tracks={this.props.tracks}
					certificates={this.props.certificates.filter((x) => currentCertificateIds.indexOf(x.id) == -1)}
					currentName={this.state.calendars.get(this.state.currentCalendar).get('name')}
					currentMajor={this.state.currentMajor}
					currentTrack={this.state.currentTrack}
					currentCertificates={this.state.currentCertificates.toJS()}
					/>

				<div className='messages-list'>
					<MessageList messages={this.state.messages.toJS()}
						onDismiss={(i) => this.setState({messages: this.state.messages.delete(i)})} />
				</div>
		</div>);
		}
	}

jQuery(document).ready(main);
