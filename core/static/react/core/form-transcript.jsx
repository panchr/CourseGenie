
var React = require('react'),
	ReactDOM = require('react-dom'),
	jQuery = require('jquery'),
	queryString = require('query-string');

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
	ListView = require('core/components/ListView.jsx'),
	ErrorAlert = require('core/components/ErrorAlert.jsx');

function main() {
	console.log('main called');
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
			transcript_data: null,
			transcript_courses: new Object(),
			added_courses: new Array(),
			errorMsg: '',
			requestErrorMsg: '',
			};
		this.elems = {};

		this.allCourses = new Array();
		}

	componentWillMount() {
		if (this.props.transcript_url) {
			this.transcriptRequest = jQuery.get(this.props.transcript_url)
				.done((data) => {
					this.setState({transcript_courses: data.transcript.courses,
						transcript_data: data});
					this.allCourses = [];
					Object.keys(data.transcript.courses).map((term) => {
						this.allCourses = this.allCourses.concat(
							data.transcript.courses[term]);
						});
					})
				.fail(() => {
					// need generic request error handling
					// - see Quizzera's utils.handleAPIError
					this.setState({requestErrorMsg: 'transcript request failed - blame Kathy'});
					})
				.always(() => {
					// probably mark off that request has finished
					});
			}
		}

	componentWillUnmount() {
		if (this.transcriptRequest) this.transcriptRequest.abort();
		}

	renderCourse(c) {
		var split = c.split(" ");
		return (<CourseDisplay department={split[0]} number={split[1]} />);
		}

	render() {
		var courses = this.state.transcript_courses;

		return (<div>
				<ErrorAlert msg={this.state.errorMsg} />
				<ErrorAlert msg={this.state.requestErrorMsg} />
				<div className="container">
					<form method="post" action="#">
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
								<a className="button button-add fit"
								onClick={() => {
									var department = this.elems.department_input.value,
										number = this.elems.number_input.value;
									var c = (department + " " + number).toUpperCase();
									this.setState({errorMsg: ''});
									if (department == '' || number == '') {
										this.setState({errorMsg: 'Cannot input a blank course'});
										}
									else if (this.allCourses.indexOf(c) != -1) {
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
											added_courses: this.state.added_courses.concat(c)
											});
										this.allCourses.push(c);
										}
									}}>Add</a>
							</div>
						</div>
					</section>
						<div className="row 50%">
							<div className="12u">
								<h1>Courses Entered</h1>
								<div className='center'> 
									<ListView t={this.renderCourse}
										data={this.state.added_courses} />
									{Object.keys(courses).map((term) => {
									return (<div key={'term-'+Math.random()}>
										<h3>{term}</h3>
										<ListView blankText='None yet!' t={this.renderCourse}
											data={courses[term]} />
										</div>);
										})}
									</div>
							</div>
						</div>
					</section>
						<div className="row 50%">
							<div className="12u">
								<a href="./form-name.html" className="button">Back</a>
								<a href="./form-interests.html" className="button">Next</a>
							</div>
						</div>
					</form>
				</div>
			</div>);
		}
	}

jQuery(document).ready(main);
