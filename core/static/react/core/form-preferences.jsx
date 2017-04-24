/*
* core/form-preferences.jsx
* Author: Rushy Panchal
* Date: April 6th, 2017
* Description: Main user preferences input form.
*/

var React = require('react'),
	ReactDOM = require('react-dom'),
	jQuery = require('jquery');

import { List } from 'immutable';

var GridView = require('core/components/GridView.jsx'),
	ErrorAlert = require('core/components/ErrorAlert.jsx'),
	Icon = require('core/components/Icon.jsx'),
	ListInput = require('core/components/ListInput.jsx'),
	CourseDisplay = require('core/components/CourseDisplay.jsx'),
	MessageList = require('core/components/MessageList.jsx'),
	data = require('core/data.jsx');

function main() {
	ReactDOM.render(<PreferenceForm />,
		document.getElementById('preference-form'));
	}

class PreferenceForm extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			bl_courses: new List(),
			bl_depts: new List(),
			wl_depts: new List(),
			bl_areas: new List(),
			wl_areas: new List(),
			messages: new List(),
			};
		this.elems = {};
		this.requests = new Array();
		this.getCourse = this.getCourse.bind(this);
		this.getDept_bl = this.getDept_bl.bind(this);
		this.getDept_wl = this.getDept_wl.bind(this);
		this.getArea_bl = this.getArea_bl.bind(this);
		this.getArea_wl = this.getArea_wl.bind(this);
		}

	addMessage(m) {
		try {
			var m_json = JSON.parse(m);
			m = m_json.detail;
			}
		catch (err) {}

		this.setState({messages: this.state.messages.push({
			message: m,
			t: 'error',
			})});
		}

	componentWillMount() {
		data.installErrorHandler((msg) => {
			this.addMessage(msg);
			this.requests.push(data.preferences.get((data) => {
				this.setState({
					bl_courses: new List(data.bl_courses.map((x) => x.short_name)),
					bl_areas: new List(data.bl_areas.map((x) => x.short_name)),
					bl_depts: new List(data.bl_depts.map((x) => x.short_name)),
					wl_depts: new List(data.wl_depts.map((x) => x.short_name)),
					wl_areas: new List(data.wl_areas.map((x) => x.short_name)),
					});
				}));
			});
		this.requests.push(data.preferences.get((data) => {
			this.setState({
				bl_courses: new List(data.bl_courses.map((x) => x.short_name)),
				bl_areas: new List(data.bl_areas.map((x) => x.short_name)),
				bl_depts: new List(data.bl_depts.map((x) => x.short_name)),
				wl_depts: new List(data.wl_depts.map((x) => x.short_name)),
				wl_areas: new List(data.wl_areas.map((x) => x.short_name)),
				});
			}));
		}

	componentWillUnmount() {
		this.requests.map((r) => r.abort());
		}

	getCourse() {
		var department = this.elems.department_input.value,
			number = this.elems.number_input.value,
			c = (department + " " + number).toUpperCase();

		if (department == '' || number == '') {
			this.addMessage('Cannot input a blank course.');
			}
		else if (this.state.bl_courses.indexOf(c) != -1) {
			this.addMessage(c + ' is already added!');
			}
		else if (! /^\w{3}$/.test(department)) {
			this.addMessage(`The department must be three letters: ${department}.`);
			}
		else if (! /^\d{3}[a-zA-Z]?$/.test(number)) {
			this.addMessage('The course number must be a number, optionally followed by a letter.');
			}
		else {
			this.state.bl_courses = this.state.bl_courses.push(c);
			this.requests.push(data.preferences.bl_course(c));
			return c;
			}
		}

	validate_dept(c) {
		return /^\w{3}$/.test(c);
		}

	validate_area(c) {
		return /^(HA|SA|LA|EM|QR|EC|STN|STL)$/.test(c);
		}

	getDept_bl() {
		var dept = this.elems.bl_dept_input.value;
		if (this.validate_dept(dept)) {
			this.state.bl_depts = this.state.bl_depts.push(dept);
			this.requests.push(data.preferences.bl_dept(dept));
			return dept;
			}
		else this.addMessage(`Department is not three letters: ${dept}.`);
		}

	getDept_wl() {
		var dept = this.elems.wl_dept_input.value;
		if (this.validate_dept(dept)) {
			this.state.wl_depts = this.state.wl_depts.push(dept);
			this.requests.push(data.preferences.wl_dept(dept));
			return dept;
			}
		else this.addMessage(`Department is not three letters: ${dept}.`);
		}

	getArea_bl() {
		var area = this.elems.bl_area_input.value;
		if (this.validate_area(area)) {
			this.state.bl_areas = this.state.bl_areas.push(area);
			this.requests.push(data.preferences.bl_area(area));
			return area;
			}
		else this.addMessage(`Not a valid distribution area: ${area}.`);
		}

	getArea_wl() {
		var area = this.elems.wl_area_input.value;
		if (this.validate_area(area)) {
			this.state.wl_areas = this.state.wl_areas.push(area);
			this.requests.push(data.preferences.wl_area(area));
			return area;
			}
		else this.addMessage(`Not a valid distribution area: ${area}.`);
		}

	render() {
		return <div>
			<div className='messages-list'>
				<MessageList messages={this.state.messages.toJS()}
					onDismiss={(i) => this.setState({messages: this.state.messages.delete(i)})} />
			</div>
			<div className="container">
				<form action="" onSubmit={(e) => e.preventDefault()}>
					<div className="row">
						<div className="12u">
							<h2>Blacklisted Courses</h2>
							<ListInput ref={(e) => this.elems.bl_courses_elem = e}
								onDelete={(c) => this.requests.push(data.preferences.del_bl_course(c))}
								t={(c) => {
								var split = c.split(" ");
								return <CourseDisplay department={split[0]} number={split[1]} />;
								}} getInput={this.getCourse} data={this.state.bl_courses} cols={2}
								blankText='None yet!'>
								<div className="6u">
									<h1>Department</h1>
								</div>
								<div className="6u$">
									<h1>Number</h1>
								</div>
								<div className="6u">
									<input placeholder="e.g. COS" type="text" className="text"
									ref={(e) => this.elems.department_input = e} />
								</div>
								<div className="6u$">
									<input placeholder="e.g. 333" type="text" className="text"
								 	ref={(e) => this.elems.number_input = e} />
									{/* refs are required (as callbacks) to get input */}
								</div>
							</ListInput>
						</div>
					</div>
					<div className="row">
						<div className="6u"><h2>Blacklisted</h2></div>
						<div className="6u"><h2>Whitelisted</h2></div>
					</div>
					<div className="row">
						<div className="6u">
							<h3>Department</h3>
							<ListInput ref={(e) => this.elems.bl_dept_elem = e}
								onDelete={(c) => this.requests.push(data.preferences.del_bl_dept(c))}
								t={(c) => <span>{c}</span>}
								getInput={this.getDept_bl} data={this.state.bl_depts} cols={2}
								blankText='None yet!'>
								<div className="12u$">
									<input placeholder="e.g. CBE" type="text" className="text"
								 	ref={(e) => this.elems.bl_dept_input = e} />
									{/* refs are required (as callbacks) to get input */}
								</div>
							</ListInput>
						</div>
						<div className="6u">
							<h3>Department</h3>
							<ListInput ref={(e) => this.elems.wl_dept_elem = e}
								onDelete={(c) => this.requests.push(data.preferences.del_wl_dept(c))}
								t={(c) => <span>{c}</span>}
								getInput={this.getDept_wl} data={this.state.wl_depts} cols={2}
								blankText='None yet!'>
								<div className="12u$">
									<input placeholder="e.g. CBE" type="text" className="text"
								 	ref={(e) => this.elems.wl_dept_input = e} />
									{/* refs are required (as callbacks) to get input */}
								</div>
							</ListInput>
						</div>
					</div>
					<div className="row">
						<div className="6u">
							<h3>Area</h3>
							<ListInput ref={(e) => this.elems.bl_area_elem = e}
								onDelete={(c) => this.requests.push(data.preferences.del_bl_area(c))}
								t={(c) => <span>{c}</span>}
								getInput={this.getArea_bl} data={this.state.bl_areas} cols={2}
								blankText='None yet!'>
								<div className="12u$">
									<input placeholder="e.g. EM" type="text" className="text"
								 	ref={(e) => this.elems.bl_area_input = e} />
									{/* refs are required (as callbacks) to get input */}
								</div>
							</ListInput>
						</div>
						<div className="6u">
							<h3>Area</h3>
							<ListInput ref={(e) => this.elems.wl_area_elem = e}
								onDelete={(c) => this.requests.push(data.preferences.del_wl_area(c))}
								t={(c) => <span>{c}</span>}
								getInput={this.getArea_wl} data={this.state.wl_areas} cols={2}
								blankText='None yet!'>
								<div className="12u$">
									<input placeholder="e.g. LA" type="text" className="text"
								 	ref={(e) => this.elems.wl_area_input = e} />
									{/* refs are required (as callbacks) to get input */}
								</div>
							</ListInput>
						</div>
					</div>
				</form>
			</div>
		</div>;
		}
	}

jQuery(document).ready(main);