/*
* core/dashboard.jsx
* Author: Rushy Panchal
* Date: April 9th, 2017
* Description: Render dashboard page.
*/

var React = require('react'),
	ReactDOM = require('react-dom');

var CourseDisplay = require('core/components/CourseDisplay.jsx'),
	ListView = require('core/components/ListView.jsx'),
	GridView = require('core/components/GridView.jsx'),
	data = require('core/data.jsx');

function main() {
	ReactDOM.render(<Dashboard />, document.getElementById('dashboard'));
	}

class Dashboard extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			semesters: new Array(),
			};

		this.elems = {};
		}

	componentWillMount() {
		this.semestersRequest = data.schedule.getSemesters((data) => {
			this.setState({semesters: data});
			});
		}

	componentWillUnmount() {
		this.semestersRequest.abort();
		}

	render() {
		return (<div className="container">
			<div className="container">
				<div className="row">
					<div className="7u">
						<h1>Schedule</h1>
						<ListView t={(e) => {
							return <div>
								<h2>{e.name}</h2>
								<GridView t={(c) => {
									return <CourseDisplay department={c.department} number={c.number} />;
									}} rows={2} cols={3} data={e.courses} />
							</div>;
							}} data={this.state.semesters}/>
					</div>
					<div className="3u">
						<h1>5 columns</h1>
					</div>
				</div>
			</div>
		</div>);
		}
	}

jQuery(document).ready(main);
