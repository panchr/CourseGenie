/*
* core/components/ErrorAlert.jsx
* Author: Rushy Panchal
*/

var React = require('react');

/*
* An alert that shows an error. It is only displayed when the error is 
* available.
*
* Optional Props
*   String header - header for error
*   String msg - message to show
*/
function ErrorAlert(props) {
  if (props.msg) {
    return (
      <div className='alert danger'>
        <h4>{props.header}</h4>
        <p>{props.msg}</p>
      </div>
      );
    }
  
  return (<span></span>);
  }

ErrorAlert.propTypes = {
  header: React.PropTypes.string,
  msg: React.PropTypes.string,
  };

ErrorAlert.defaultProps = {
  header: "Error",
  msg: null,
  };

module.exports = ErrorAlert;
