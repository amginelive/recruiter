import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from './actions/index.js';
import UserList from './user-list.jsx';
import MessageList from './message-list.jsx';
import MessageForm from './message-send-form.jsx';
import TypingList from './typing-list.jsx';
import GroupChatModal from './group-chat-modal.jsx';

import '../css/chat.scss';


class App extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            chatInitPending: false,
            showModal: false
        };
    }

    setChatInitPendingState(state) {
        this.setState({chatInitPending: state});
    }

    handleOpenModal () {
        this.setState({ showModal: true });
    }

    handleCloseModal () {
        this.setState({ showModal: false });
    }

    render() {
        return (
            <div className='app-container'>
                <GroupChatModal showModal={this.state.showModal} onClose={this.handleCloseModal.bind(this)} />
                <div className ='chat-container'>
                    <UserList createGroupModal={this.handleOpenModal.bind(this)} setChatInitPendingState={this.setChatInitPendingState.bind(this)} />
                    <div className='app-inner-column'>
                        <MessageList setChatInitPendingState={this.setChatInitPendingState.bind(this)}
                                     chatInitPending={this.state.chatInitPending}
                        />
                        <TypingList />
                        <MessageForm />
                    </div>
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
