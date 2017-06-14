import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from './actions/index.js';
import UserList from './user-list.jsx';
import MessageList from './message-list.jsx';
import MessageForm from './message-send-form.jsx';
import TypingList from './typing-list.jsx';

import '../css/chat.scss';


class App extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            chatInitPending: false
        };
    }

    setChatInitPendingState(state) {
        this.setState({chatInitPending: state});
    }

    render() {
        return (
            <div className='app-container'>
                <div className ='chat-container'>
                    <div className='app-inner-row'>
                        <UserList setChatInitPendingState={this.setChatInitPendingState.bind(this)} />
                        <MessageList setChatInitPendingState={this.setChatInitPendingState.bind(this)}
                                     chatInitPending={this.state.chatInitPending}
                        />
                    </div>
                    <TypingList />
                    <MessageForm />
                </div>
                <div className='placeholder'></div>
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        messages: state.get('messages'),
        typing: state.get('typing')
    };
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
)(App);
