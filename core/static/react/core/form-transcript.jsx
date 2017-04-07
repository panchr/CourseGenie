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

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
	ListView = require('core/components/ListView.jsx'),
	ErrorAlert = require('core/components/ErrorAlert.jsx'),
	Icon = require('core/components/Icon.jsx');

function main() {
	var queryParameters = queryString.parse(window.location.search);
	var ticket = queryParameters.ticket;

	if (ticket) {
		var url = transcript_url + ticket;
		}
	else {
		var url = '';
		}
	ReactDOM.render(<CourseForm transcript_url={url} />,
		document.getElementById('course-form'));
	}

class CourseForm extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			courses: new Array(),
			user: new Object(),
			errorMsg: '',
			requestErrorMsg: '',
			};
		this.elems = {};
		this.renderCourse = this.renderCourse.bind(this);
		this.removeCourse = this.removeCourse.bind(this);
		this.addCourse = this.addCourse.bind(this);
		this.submitForm = this.submitForm.bind(this);
		}

	componentWillMount() {
		if (this.props.transcript_url) {
			this.transcriptRequest = jQuery.get(this.props.transcript_url)
				.done((data) => {
					var courses = [];
					for (var term in data.transcript.courses) {
						courses = courses.concat(data.transcript.courses[term]);
						}
					this.setState({courses: courses, user: data.user});
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

	renderCourse(c) {
		var split = c.split(" ");
		return (<div>
			<CourseDisplay department={split[0]} number={split[1]} />
			&nbsp;
			<Icon i='ios-close-outline' onClick={() => {this.removeCourse(c)}}
				style={{color: 'red'}} className='btn' />
			</div>);
		}

	removeCourse(c) {
		this.setState({courses: this.state.courses.filter((x) => x != c)});
		}

	addCourse(c) {
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
		else if (! /^\d{3}\w?$/.test(number)) {
			this.setState({errorMsg: 'The course number must be a number, optionally followed by a letter.'});
			}
		else {
			this.setState({
				// need to use concat instead of push to return a new
				// array, which signals an update.
				courses: this.state.courses.concat(c)
				});
			}
		}

	submitForm(event) {
		var data = {
			courses: this.state.courses,
			user: {
				first_name: this.elems.first_name_input.value,
				last_name: this.elems.last_name_input.value,
				},
			graduation_year: this.elems.year_input.value
			};
		event.preventDefault();
		}

	render() {
		return (<div>
				<ErrorAlert msg={this.state.errorMsg} />
				<ErrorAlert msg={this.state.requestErrorMsg} />
				<div className="container">
					<form method="post" action="" onSubmit={this.submitForm}>
						<section><section>
						<div className="row 50%">
							<div className="3u">
								<h1>Department</h1>
							</div>
							<div className="3u$">
								<h1>Number</h1>
							</div>
							<div className="3u">
								<input placeholder="COS" type="text" className="text"
								ref={(e) => this.elems.department_input = e} />
							</div>
							<div className="3u">
								<input placeholder="333" type="text" className="text"
							 	ref={(e) => this.elems.number_input = e} />
								{/* refs are required (as callbacks) to get input */}
							</div>
							<div className="3u">
								<a className="button button-add fit btn"
									onClick={this.addCourse}>Add</a>
							</div>
						</div>
					</section>
						<div className="row 50%">
							<div className="12u">
								<h1>Courses Entered</h1>
								<div className='center'> 
									<ListView t={this.renderCourse} data={this.state.courses}
										blankText='None yet!' />
								</div>
							</div>
						</div>
					<hr/>
					<div className="row 50%">
						<div className="6u"><h1>First Name</h1></div>
						<div className="6u$"><h1>Last Name</h1></div>
						<div className="6u">
							<input type="text"
							ref={(e) => this.elems.first_name_input = e} />
						</div>
						<div className="6u">
							<input type="text"
								ref={(e) => this.elems.last_name_input = e} />
						</div>
					</div>
					<div className="row 50%">
						<div className="6u$">
							<h1>Graduation Year</h1>
						</div>
						<div className="6u">
							<input defaultValue={(new Date()).getFullYear() + 3}
								type="number" className="number"
								ref={(e) => this.elems.year_input = e} />
						</div>
					</div>
					</section>
						<div className="row 50%">
							<div className="12u center">
								<input type="submit" className="button btn" value="Get Started"/>
							</div>
						</div>
					</form>
				</div>
			</div>);
		}
	}

jQuery(document).ready(main);
