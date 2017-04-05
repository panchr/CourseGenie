
var React = require('react'),
	ReactDOM = require('react-dom'),
	jQuery = require('jquery'),
	queryString = require('query-string');

var CourseDisplay = require('core/components/CourseDisplay.jsx');

function main() {
	var queryParameters = queryString.parse(window.location.search);
	var ticket = queryParameters.ticket;

	if (ticket) {
		var url = transcript_url + ticket;
		// var request = jQuery.get(url)
		var request = jQuery.get(url)
			.done((data) => {
				// do something with the data
				console.log(data);
				var courses = data.transcript.courses;
				var elem = (<div>{
					Object.keys(courses).map((term) => {
						return (<div key={'term-'+Math.random()}>
							<h3>{term}</h3>
							{courses[term].map((c) => {
								var split = c.split(" ");
								return (<div>
									<CourseDisplay department={split[0]}
									number={split[1]}
									key={'course-' + Math.random()} />
									<br/>
									</div>);
							})}
						</div>);	
					})
				}</div>);
				ReactDOM.render(elem, document.getElementById('added-courses'));
				})
			.fail(() => {
				// need generic request error handling
				// - see Quizzera's utils.handleAPIError
				console.log('transcript request failed - blame Kathy');
				})
			.always(() => {
				// probably mark off that request has finished
				});
		}
	}

main();
