import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from './actions/index.js';
import UserList from './user-list.jsx';
import MessageList from './message-list.jsx';
import MessageForm from './message-send-form.jsx';
import TypingList from './typing-list.jsx';
import CreateGroupChatModal from './create-group-chat-modal.jsx';
import LeaveGroupChatModal from './leave-group-chat-modal.jsx';
import InfoGroupChatModal from './info-group-chat-modal.jsx';
import ChatHeader from './chat-header.jsx';

import '../css/chat.scss';


class App extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            chatInitPending: false,
            showCreateGroupChatModal: false,
            showLeaveGroupChatModal: false,
            showInfoGroupChatModal: false
        };
    }

    setChatInitPendingState(state) {
        this.setState({chatInitPending: state});
    }

    handleOpenCreateGroupChatModal () {
        this.setState({showCreateGroupChatModal: true});
    }

    handleCloseCreateGroupChatModal () {
        this.setState({showCreateGroupChatModal: false});
    }

    handleOpenLeaveGroupChatModal () {
        this.setState({showLeaveGroupChatModal: true});
    }

    handleCloseLeaveGroupChatModal () {
        this.setState({showLeaveGroupChatModal: false});
    }

    handleOpenInfoGroupChatModal () {
        this.setState({showInfoGroupChatModal: true});
    }

    handleCloseInfoGroupChatModal () {
        this.setState({showInfoGroupChatModal: false});
    }

    handleCreateGroup(user_ids, name, message) {
        this.props.actions.createGroup({user_ids, name, message});
        this.setState({showCreateGroupChatModal: false});
    }

    handleLeaveGroup() {
        this.props.actions.leaveGroup();
        this.setState({showLeaveGroupChatModal: false});
    }

    handleKickUser(user_id) {
        this.props.actions.kickUser(user_id);
    }

    handleInviteUsers(payload) {
        this.props.actions.inviteUsers(payload);
    }

    render() {
        return (
            <div className='app-container'>
                <CreateGroupChatModal
                    showModal={this.state.showCreateGroupChatModal}
                    onClose={this.handleCloseCreateGroupChatModal.bind(this)}
                    onCreate={this.handleCreateGroup.bind(this)}
                    users={this.props.users}
                />
                <LeaveGroupChatModal
                    showModal={this.state.showLeaveGroupChatModal}
                    onClose={this.handleCloseLeaveGroupChatModal.bind(this)}
                    onLeave={this.handleLeaveGroup.bind(this)}
                />
                <InfoGroupChatModal
                    showModal={this.state.showInfoGroupChatModal}
                    onClose={this.handleCloseInfoGroupChatModal.bind(this)}
                    onKick={this.handleKickUser.bind(this)}
                    onInvite={this.handleInviteUsers.bind(this)}
                    users={this.props.users}
                    chats={this.props.chats}
                />
                <div className ='chat-container'>
                    <UserList createGroupModal={this.handleOpenCreateGroupChatModal.bind(this)} setChatInitPendingState={this.setChatInitPendingState.bind(this)} />
                    <div className='app-inner-column'>
                        <ChatHeader
                            leaveGroupModal={this.handleOpenLeaveGroupChatModal.bind(this)}
                            infoGroupModal={this.handleOpenInfoGroupChatModal.bind(this)}
                        />
                        <MessageList
                            setChatInitPendingState={this.setChatInitPendingState.bind(this)}
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
        users: state.get('users'),
        chats: state.get('chats')
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
