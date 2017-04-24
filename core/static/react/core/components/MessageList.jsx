/*
* core/components/MessageList.jsx
* Author: Rushy Panchal
* Date: April 19th, 2017
* Description: Provides a list of dismissable messages.
*/

var React = require('react');

var ListView = require('core/components/ListView.jsx'),
	Icon = require('core/components/Icon.jsx');

import { List } from 'immutable';

function MessageList(props) {
	return <ListView t={(e, i) => {
		if (typeof e == "string") e = {header: '', message: e, t: 'default'};
				return <div className={`message ${e.t}`}>
					<h1>{e.header}</h1>
					<Icon i='ios-close-empty' className='btn large-icon'
						style={{color: 'LightSlateGray', float: 'right'}}
						onClick={() => props.onDismiss(i)} />
					<br/>
					<span>{e.message}</span>
				</div>;
		}}
		data={props.messages} />;
	}

MessageList.propTypes = {
	messages: React.PropTypes.arrayOf(React.PropTypes.oneOfType([
		React.PropTypes.shape({
	    header: React.PropTypes.string,
	    t: React.PropTypes.string,
	    message: React.PropTypes.string.isRequired,
	  }),
	  React.PropTypes.string.isRequired,
		])).isRequired,
	onDismiss: React.PropTypes.func.isRequired,
	};

MessageList.defaultProps = {
	dismissable: true,
	};

module.exports = MessageList;
