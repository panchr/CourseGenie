
var jQuery = require('jquery'),
	queryString = require('query-string');

function main() {
	var queryParameters = queryString.parse(window.location.search);
	var ticket = queryParameters.ticket;

	if (ticket) {
		var url = transcript_url + ticket;
		// var request = jQuery.get(url)
		var request = jQuery.ajax({
			'url': url,
			type: 'GET',
			crossDomain: true,
			headers: {
				'Access-Control-Allow-Headers': 'x-requested-with',
			}
			})
			.done((data) => {
				// do something with the data
				console.log(data);
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
