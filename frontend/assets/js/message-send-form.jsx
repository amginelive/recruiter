import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from './actions/index.js';


class MessageForm extends React.Component {
    constructor(props){
        super(props);

        this.state = { valid: false, message: '' };
    }

    onSend(event) {
        event.preventDefault();
        if (!this.state.valid) {
            return;
        }

        this.props.actions.sendMessage(this.state.message);
        this.setState({valid: false, message: ''});
    }

    checkInput(event) {
        const message = event.target.value;
        const valid = message && message.length > 0;
        this.setState({ valid, message });
    }

    render() {
        const submitDisabled = !this.state.valid;
        return (
            <form id='message-form' onSubmit={this.onSend.bind(this)}>
                <input className='message-input'
                       ref={input => this.textInput = input}
                       type='text'
                       placeholder='Say something nice'
                       maxLength='1024'
                       onChange={this.checkInput.bind(this)}
                       onKeyDown={this.checkInput.bind(this)}
                       value={this.state.message}
                />
                <button className='send-button' type='submit' disabled={submitDisabled}>
                    Send
                </button>
            </form>
        );
    }
}

function mapStateToProps (state) {
    return {};
}

function mapDispatchToProps (dispatch) {
    return {
        dispatch: dispatch,
        actions: bindActionCreators(actions, dispatch)
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(MessageForm);
