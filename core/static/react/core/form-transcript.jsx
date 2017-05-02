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
	ListInput = require('core/components/ListInput.jsx');

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
			graduation_year: props.data.graduation_year,
			errorMsg: '',
			requestErrorMsg: '',
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
					this.setState({courses: new List(courses),
						user: data.user});
					this.elems.first_name_input.value = data.user.first_name;
					this.elems.last_name_input.value = data.user.last_name;
					})
				.fail(() => {
					// need generic request error handling
					// - see Quizzera's utils.handleAPIError
					this.setState({requestErrorMsg: 'transcript request failed - blame Kathy'});
					});
			}
		}

	componentWillUnmount() {
		if (this.transcriptRequest) this.transcriptRequest.abort();
		}

	getCourse(c) {
		var department = this.elems.department_input.value,
			number = this.elems.number_input.value,
			c = (department + " " + number).toUpperCase();

		this.setState({errorMsg: ''});

		if (department == '' || number == '') {
			this.setState({errorMsg: 'Cannot input a blank course'});
			}
		else if (this.state.courses.indexOf(c) != -1) {
			this.setState({errorMsg: c + ' is already added!'});
			}
		else if (! /^\w{3}$/.test(department)) {
			this.setState({errorMsg: 'The department must be 3 letters.'});
			}
		else if (! /^\d{3}[a-zA-Z]?$/.test(number)) {
			this.setState({errorMsg: 'The course number must be a number, optionally followed by a letter.'});
			}
		else {
			return c;
			}
		}

	submitForm(event) {
		var data = {
			courses: this.elems.courses_list.getValues(),
			user: {
				first_name: this.elems.first_name_input.value,
				last_name: this.elems.last_name_input.value,
				},
			graduation_year: this.elems.year_input.value,
			major: this.elems.major_input.value,
			};

		if (data.user.first_name == '' || data.user.last_name == '') {
			event.preventDefault(); // prevent form submission
			this.setState({errorMsg: 'A first and last name must be provided!'});
			}

		this.elems.data_out.value = JSON.stringify(data);
		}

	render() {
		var hiddenIfSubmitted = {};
		var hiddenIfNotSubmitted = {};
		if (this.props.data.submitted) hiddenIfSubmitted.display = 'none';
		if (!this.props.data.submitted) hiddenIfNotSubmitted.display = 'none';

		return (<div>
				<ErrorAlert msg={this.state.errorMsg} />
				<ErrorAlert msg={this.state.requestErrorMsg} />
				<div className="container">
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
									}} getInput={this.getCourse} data={this.state.courses} cols={4} blankText='None yet!' >
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
							<input type="text" defaultValue={this.state.user.first_name}
							ref={(e) => this.elems.first_name_input = e} />
						</div>
						<div className="6u">
							<input type="text" defaultValue={this.state.user.last_name}
								ref={(e) => this.elems.last_name_input = e} />
						</div>
					</div>
					<div className="row">
						<div className="6u$">
							<h1>Graduation Year</h1>
						</div>
						<div className="6u">
							<input defaultValue={
								this.state.graduation_year || (new Date()).getFullYear() + 3}
								type="number" className="number"
								ref={(e) => this.elems.year_input = e} />
						</div>
					</div>
					<div className="row" style={hiddenIfSubmitted}>
						<div className="12u$">
							<h1>Major (can be changed later)</h1>
						</div>
						<div className="12u">
							<select name="selected-major"
								ref={(e) => this.elems.major_input = e}>
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
								<input type="submit" className="button btn" value="Submit"/>
								<div className='topbtm-pad'></div>
							</div>
						</div>
					</form>
				</div>
			</div>);
		}
	}

jQuery(document).ready(main);
