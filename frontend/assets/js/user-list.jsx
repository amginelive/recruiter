import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Scrollbars } from 'react-custom-scrollbars';
import moment from 'moment';
import { Loader } from 'react-loaders';

import * as actions from './actions/index.js';


class UserList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            userPresencePollingInterval: 10,
            selectedUsersGroup: 0
        };
        setInterval(() => this.props.actions.userPresence(), this.state.userPresencePollingInterval*1000);
    }

    componentWillReceiveProps(nextProps) {
        const activeChat = nextProps.chats.get('activeChat');
        if (this.props.chats.get('activeChat') !== activeChat) {
            ['candidates', 'agents', 'groups'].some((group, index) => {
                const value = nextProps.chats.get(group).find((chat, conversation_id) => parseInt(conversation_id) === activeChat);
                if (value) {
                    this.setState({selectedUsersGroup: index});
                    return true;
                } else return false;
            });
        }
    }

    chatInit(id) {
        if (parseInt(id) === this.props.chats.get('activeChat')) {
            return;
        }
        this.props.setChatInitPendingState(true);
        this.props.actions.initChat(id);
    }

    formatDate(date) {
        const now = moment();
        const then = moment(date);
        if (then.isSame(now, 'day')) {
            return then.format('h:mm a');
        } else {
            return then.format('l');
        }
    }

    renderUsersGroup(chats, group_name) {
        if (this.props.users.get('self') === 0) {
            return <Loader className='empty-user-group' type='ball-pulse' active />;
        }
        if (chats.size === 0) {
            return <div className='empty-user-group'>You have no {group_name}</div>
        }
        const {users} = this.props;
        return chats.map((chat, conversation_id) => {
            const show_last_message = chat.get('last_message_text') !== '';
            // TODO: Figure out something for group avatar.
            return (
                <div
                    onClick={() => {this.chatInit(conversation_id)}}
                    key={conversation_id}
                    className={'user-list-item' + (parseInt(conversation_id) === this.props.chats.get('activeChat') ? ' active' : '')}
                >
                    {chat.get('user') ?
                        <div className={'user-avatar' + (users.get(chat.get('user').toString()).get('online') === 2 ? ' user-online' : (users.get(chat.get('user').toString()).get('online') === 1 ? ' user-away': ''))}>
                            <img src={users.get(chat.get('user').toString()).get('photo')} />
                        </div> :
                        <div className='group-avatar'>
                            <img src={users.get(users.get('self').toString()).get('photo')} />
                        </div>
                    }
                    <div className='user-list-item-pane'>
                        <div className='user-list-item-pane-row'>
                            <span className='user-list-item-name'>{chat.get('name')}</span>
                            {show_last_message ? <span className='user-list-item-timestamp'>{this.formatDate(chat.get('last_message_time'))}</span> : ''}
                        </div>
                        <div className='user-list-item-pane-row'>
                            {show_last_message ? <span className='user-list-item-message'>{chat.get('last_message_text')}</span> : ''}
                            {chat.get('unread') > 0 ? <div className='user-list-item-unread'><span>{chat.get('unread')}</span></div> : ''}
                        </div>
                    </div>
                </div>
            );
        }).toArray();
    }

    handleUserGroupSelect(group) {
        this.setState({selectedUsersGroup: group});
    }

    render() {
        const {chats} = this.props;
        const unreadCandidates = chats.get('candidates').reduce((result, user) => result + user.get('unread'), 0);
        const unreadAgents = chats.get('agents').reduce((result, user) => result + user.get('unread'), 0);
        const unreadGroups = chats.get('groups').reduce((result, user) => result + user.get('unread'), 0);

        let userListUI = '';
        if (this.state.selectedUsersGroup === 0) {
            userListUI = this.renderUsersGroup(chats.get('candidates'), 'team network connections');
        } else if (this.state.selectedUsersGroup === 1) {
            userListUI = this.renderUsersGroup(chats.get('agents'), 'agents connections');
        } else {
            userListUI = this.renderUsersGroup(chats.get('groups'), 'group conversations');
        }

        return (
            <div className='user-list-container'>
                <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                                style={{height: '100%'}}
                                autoHide autoHideTimeout={1000}
                                autoHideDuration={200}>
                    <div className='user-list'>
                        <div className='user-list-header'>
                            <button className={'chat-button user-list-button button-candidates' + (this.state.selectedUsersGroup === 0 ? ' active' : '')} onClick={this.handleUserGroupSelect.bind(this, 0)}>
                                Candidates
                                {
                                    this.state.selectedUsersGroup !== 0 && unreadCandidates !== 0 ?
                                    <span>{unreadCandidates}</span> :
                                    ''
                                }
                            </button>
                            <button className={'chat-button user-list-button button-agents' + (this.state.selectedUsersGroup === 1 ? ' active' : '')} onClick={this.handleUserGroupSelect.bind(this, 1)}>
                                Agents
                                {
                                    this.state.selectedUsersGroup !== 1 && unreadAgents !== 0 ?
                                    <span>{unreadAgents}</span> :
                                    ''
                                }
                            </button>
                            <button className={'chat-button user-list-button button-groups' + (this.state.selectedUsersGroup === 2 ? ' active' : '')} onClick={this.handleUserGroupSelect.bind(this, 2)}>
                                Groups
                                {
                                    this.state.selectedUsersGroup !== 2 && unreadGroups !== 0 ?
                                    <span>{unreadGroups}</span> :
                                    ''
                                }
                            </button>
                        </div>
                        <div className='user-list-group'>
                            {userListUI}
                            {this.state.selectedUsersGroup === 2 ? <span onClick={this.props.createGroupModal} id='create-conversation' className='glyphicon glyphicon-plus'></span> : ''}
                        </div>
                    </div>
                </Scrollbars>
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
)(UserList);
