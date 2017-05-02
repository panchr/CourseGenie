/*
* core/components/CalendarSettings.jsx
* CourseGenie
* Author: Rushy Panchal
* Date: May 2nd, 2017
* Description: Calendar settings modal.
*/

const React = require('react'),
	classNames = require('classnames');

const Modal = require('core/components/Modal.jsx'),
	ListInput = require('core/components/ListInput.jsx');

class CalendarSettings extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			currentMajor: props.currentMajor,
			currentTrack: props.currentTrack,
			currentCertificates: props.currentCertificates,
			};
		this.elems = {};
		}

	componentWillReceiveProps(newProps) {
		if (newProps != this.props) this.setState({
			currentMajor: newProps.currentMajor,
			currentTrack: newProps.currentTrack,
			currentCertificates: newProps.currentCertificates,
			});
		}

	onSave() {
		var data = {
			name: this.elems.name_input.value,
			major: this.elems.major_input.value,
			track: this.elems.track_input.value == 'null' ? null: this.elems.track_input.value,
			};

		// Remove track if not found in the current major.
		var trackInMajor = false;
		for (var i=0; i < this.props.tracks[data.major].length; i++) {
			var t = this.props.tracks[data.major][i];
			if (t.id == data.track) {
				trackInMajor = true;
				break;
				}
			}

		if (! trackInMajor) data.track = null;

		this.setState({open: false});
		this.props.onSave(data);
		}

	render() {
		const majorTrackSize = this.props.addMode ? '12u': '6u',
			certificateSize = this.props.addMode ? '0u': '6u';

		var certificateStyle = {};
		if (this.props.addMode) certificateStyle.display = 'none';

		return 	<Modal open={this.props.open}
			buttonText={this.props.addMode? 'Add': 'Save'}
			onButtonClick={() => this.onSave()}
			onClose={() => this.props.onClose()}
			className={classNames({'center-parent': true, 'expanding': ! this.props.addMode})}>
			<h1>{this.props.header}</h1>
			<div className='row'>
				<div className='12u'>
					<h2>Name</h2>
				</div>
			</div>
			<div className='row no-children-top-padding'>
				<div className="12u">
					<input type="text" className="text fit"
					defaultValue={this.props.currentName}
					ref={(e) => this.elems.name_input = e} maxLength="50" />
				</div>
			</div>

			<div className="row">
				<div className={majorTrackSize}>
					<div className="row no-children-top-padding">
						<div className="12u"><h2>Major</h2></div>
						<div className="12u center">
							<select name="add-selected-major"
								value={this.state.currentMajor}
								onChange={(e) => this.setState({currentMajor: e.target.value})}
								ref={(e) => this.elems.major_input = e}>
								{this.props.majors.map((e) =>
									<option value={e.id} key={Math.random()}>{e.name}</option>)}
							</select>
						</div>
					</div>
					<div className="row no-children-top-padding">
						<div className="12u"><h2>Track</h2></div>
					</div>
					<div className="row no-children-top-padding">
						<div className="12u center">
							<select name="selected-track" defaultValue={this.state.currentTrack}
								ref={(e) => this.elems.track_input = e}>
								<option value="null">None</option>
								{this.props.tracks[this.state.currentMajor].map((e) =>
									<option value={e.id} key={Math.random()}>{e.name}</option>)}
							</select>
						</div>
					</div>
				</div>

				<div className={certificateSize} style={certificateStyle}>
					<div className="row no-children-top-padding">
						<div className="12u"><h2>Certificate(s)</h2></div>
					</div>
					<div className="row">
						<div className="12u center">
							<ListInput t={(e) => <span>{e.name}</span>}
								data={this.state.currentCertificates}
								blankText='None yet!'
								getInput={() => this.props.certificates[this.elems.certificate_input.value]} cols={2}
								onAdd={(e) => this.props.onCertificateAdd(e)}
								onDelete={(e, i) => this.props.onCertificateRemove(e, i)}>
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
				</div>
			</div>
		</Modal>;
		}
	}

const ConcentrationPropType = React.PropTypes.shape({
	id: React.PropTypes.number,
	name: React.PropTypes.string,
	});

CalendarSettings.propTypes = {
	open: React.PropTypes.bool.isRequired,
	majors: React.PropTypes.arrayOf(ConcentrationPropType).isRequired,
	tracks: React.PropTypes.objectOf(
		React.PropTypes.arrayOf(ConcentrationPropType)
		).isRequired,
	certificates: React.PropTypes.arrayOf(ConcentrationPropType).isRequired,
	header: React.PropTypes.string.isRequired,
	currentMajor: React.PropTypes.number,
	currentTrack: React.PropTypes.number,
	currentName: React.PropTypes.string,
	currentCertificates: React.PropTypes.arrayOf(React.PropTypes.number).isRequired,
	onSave: React.PropTypes.func,
	onClose: React.PropTypes.func,
	onCertificateAdd: React.PropTypes.func,
	onCertificateRemove: React.PropTypes.func,
	addMode: React.PropTypes.bool,
	};

CalendarSettings.defaultProps = {
	currentMajor: null,
	currentTrack: null,
	currentName: 'New Calendar',
	onSave: () => null,
	onClose: () => null,
	onCertificateAdd: () => null,
	onCertificateRemove: () => null,
	addMode: false,
	};

module.exports = CalendarSettings;
