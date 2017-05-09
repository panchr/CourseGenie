/*
* core/form-transcript.jsx
* Author: Rushy Panchal
* Date: April 6th, 2017
* Description: Main user input form.
*/

var React = require('react'),
	ReactDOM = require('react-dom'),
	jQuery = require('jquery'),
	queryString = require('query-string');

import { List } from 'immutable';

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
	GridView = require('core/components/GridView.jsx'),
	ErrorAlert = require('core/components/ErrorAlert.jsx'),
	Icon = require('core/components/Icon.jsx'),
	ListInput = require('core/components/ListInput.jsx'),
	MessageList = require('core/components/MessageList.jsx');

function main() {
	var queryParameters = queryString.parse(window.location.search);
	var ticket = queryParameters.ticket;

	if (ticket) {
		var url = transcript_data.url + ticket;
		}
	else {
		var url = '';
		}

	var majors = [];
	for (var index in transcript_data.majors) {
		var major_data = transcript_data.majors[index];
		majors.push({label: major_data.short_name + ' - ' + major_data.name,
			value: major_data.id});
		}

	ReactDOM.render(<CourseForm transcript_url={url}
		action={transcript_data.form_action} majors={majors}
		data={transcript_data.existing_data} />,
		document.getElementById('course-form'));
	}

class CourseForm extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			courses: new List(props.data.existing_courses),
			user: props.data.user,
			messages: new List(),
			graduation_year: props.data.graduation_year || (new Date()).getFullYear() + 3,
			major: props.majors[0].value,
			first_name: props.data.user.first_name,
			last_name: props.data.user.last_name,
			};

		this.elems = {};
		this.submitForm = this.submitForm.bind(this);
		this.getCourse = this.getCourse.bind(this);
		}

	componentWillMount() {
		if (this.props.transcript_url) {
			this.transcriptRequest = jQuery.get(this.props.transcript_url)
				.done((data) => {
					var courses = [];
					for (var term in data.transcript.courses) {
						courses = courses.concat(data.transcript.courses[term]);
						}
					this.setState({courses: new List(courses), user: data.user,
						first_name: data.user.first_name, last_name: data.user.last_name});
					})
				.fail(() => {
					// need generic request error handling
					// - see Quizzera's utils.handleAPIError
					this.addMessage({message: 'Please re-submit transcript.', t: 'error'});
					});
			}
		}

	componentWillUnmount() {
		if (this.transcriptRequest) this.transcriptRequest.abort();
		}

	addMessage(m) {
		this.setState({messages: this.state.messages.push(m)});
		}

	getCourse(c) {
		var department = this.elems.department_input.value,
			number = this.elems.number_input.value,
			c = (department + " " + number).toUpperCase();

		if (department == '' || number == '') {
			this.addMessage({message: 'Cannot input a blank course', t: 'error'});
			}
		else if (this.state.courses.indexOf(c) != -1) {
			this.addMessage({message: c + ' is already added!', t: 'error'});
			}
		else if (! /^\w{3}$/.test(department)) {
			this.addMessage({message: 'The department must be 3 letters.', t: 'error'});
			}
		else if (! /^\d{3}[a-zA-Z]?$/.test(number)) {
			this.addMessage({message: 'The course number must be a number, optionally followed by a letter.', t: 'error'});
			}
		else {
			return c;
			}
		}

	submitForm(event) {
		var data = {
			courses: this.elems.courses_list.getValues(),
			user: {
				first_name: this.state.first_name,
				last_name: this.state.last_name,
				},
			graduation_year: this.state.graduation_year,
			major: this.state.major,
			};

		if (data.user.first_name == '' || data.user.last_name == '') {
			event.preventDefault(); // prevent form submission
			this.addMessage({message: 'A first and last name must be provided!', t: 'error'});
			}

		this.elems.data_out.value = JSON.stringify(data);
		}

	render() {
		var hiddenIfSubmitted = {};
		var hiddenIfNotSubmitted = {};
		if (this.props.data.submitted) hiddenIfSubmitted.display = 'none';
		if (!this.props.data.submitted) hiddenIfNotSubmitted.display = 'none';

		return (<div>
				<div className="container">
					<div className='messages-list'>
						<MessageList messages={this.state.messages.toJS()}
							onDismiss={(i) => this.setState({messages: this.state.messages.delete(i)})} />
					</div>

					<form method="post" action={this.props.action}
						onSubmit={this.submitForm}>
						<section><section>
						<input type="hidden" name="data"
							ref={(e) => this.elems.data_out = e} />
						<input type="hidden" name="csrfmiddlewaretoken"
							value={window._csrf_token}/>
						<div className="row">
							<div className="12u">
								<ListInput ref={(e) => this.elems.courses_list = e} t={(c) => {
									var split = c.split(" ");
									return <CourseDisplay department={split[0]} number={split[1]} />;
									}} getInput={this.getCourse} data={this.state.courses} cols={4} blankText='None yet!'
									onAdd={(e) => this.setState({courses: this.state.courses.push(e)})}
									onDelete={(e, i) => this.setState({courses: this.state.courses.remove(i)})}>
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
					</section>
					<hr/>
					<div className="row">
						<div className="6u"><h1>First Name</h1></div>
						<div className="6u$"><h1>Last Name</h1></div>
						<div className="6u">
							<input type="text" value={this.state.first_name}
								onChange={(e) => this.setState({first_name: e.target.value})}
								maxLength="25" />
						</div>
						<div className="6u">
							<input type="text" value={this.state.last_name}
								onChange={(e) => this.setState({last_name: e.target.value})}
								maxLength="25" />
						</div>
					</div>
					<div className="row">
						<div className="6u$">
							<h1>Graduation Year</h1>
						</div>
						<div className="6u">
							<input value={this.state.graduation_year}
								onChange={(e) => this.setState({graduation_year: e.target.value})}
								type="text" className="number" />
						</div>
					</div>
					<div className="row" style={hiddenIfSubmitted}>
						<div className="12u$">
							<h1>Major (can be changed later)</h1>
						</div>
						<div className="12u">
							<select name="selected-major" value={this.state.major}
								onChange={(e) => this.setState({major: e.target.value})}>
								{this.props.majors.map((e) =>
									<option value={e.value} key={Math.random()}>{e.label}</option>)}
							</select>
						</div>
					</div>
					</section>
						<div className="row 50%" style={hiddenIfSubmitted}>
							<div className="12u center">
								<input type="submit" className="button btn" value="Get Started"/>
								<div className='topbtm-pad'></div>
							</div>
						</div>
						<div className="row 50%" style={hiddenIfNotSubmitted}>
							<div className="12u center">
								<input type="submit" className="button btn" value="Save"/>
								<div className='topbtm-pad'></div>
							</div>
						</div>
					</form>
				</div>
			</div>);
		}
	}

jQuery(document).ready(main);
