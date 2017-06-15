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
        const activeChat = nextProps.users.get('activeChat');
        if (this.props.users.get('activeChat') === 0 && activeChat !== 0) {
            ['candidates', 'agents'].some((group, index) => {
                const value = nextProps.users.get(group).find(user => user.get('conversation_id') === activeChat);
                if (value) {
                    this.setState({selectedUsersGroup: index});
                    return true;
                } else return false;
            });
        }
    }

    userInit(id) {
        if (id === this.props.users.get('activeChat')) {
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

    renderUsersGroup(users, group_name) {
        if (this.props.users.get('self') === 0) {
            return <Loader className='empty-user-group' type='ball-pulse' active />;
        }
        if (users.size === 0) {
            return <div className='empty-user-group'>You have no {group_name} connections</div>
        }
        return users.map(user => {
            const show_last_message = moment(user.get('last_message_time')).valueOf() > 60*60*24;
            return (
                <div
                    onClick={() => {this.userInit(user.get('conversation_id'))}}
                    key={user.get('conversation_id')}
                    className={'user-list-item' + (user.get('conversation_id') === this.props.users.get('activeChat') ? ' active' : '')}
                >
                    <div className={'user-avatar' + (user.get('online') === 2 ? ' user-online' : (user.get('online') === 1 ? ' user-away': ''))}>
                        <img src={user.get('photo')} />
                    </div>
                    <div className='user-list-item-pane'>
                        <div className='user-list-item-pane-row'>
                            <span className='user-list-item-name'>{user.get('name')}</span>
                            {show_last_message ? <span className='user-list-item-timestamp'>{this.formatDate(user.get('last_message_time'))}</span> : ''}
                        </div>
                        <div className='user-list-item-pane-row'>
                            {show_last_message ? <span className='user-list-item-message'>{user.get('last_message_text')}</span> : ''}
                            {user.get('unread') > 0 ? <div className='user-list-item-unread'><span>{user.get('unread')}</span></div> : ''}
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
        const { users } = this.props;
        const unread_candidates = this.props.users.get('candidates').reduce((result, user) => result + user.get('unread'), 0);
        const unread_agents = this.props.users.get('agents').reduce((result, user) => result + user.get('unread'), 0);
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
                                    this.state.selectedUsersGroup !== 0 && unread_candidates !== 0 ?
                                    <span>{unread_candidates}</span> :
                                    ''
                                }
                            </button>
                            <button className={'chat-button user-list-button button-agents' + (this.state.selectedUsersGroup === 1 ? ' active' : '')} onClick={this.handleUserGroupSelect.bind(this, 1)}>
                                Agents
                                {
                                    this.state.selectedUsersGroup !== 1 && unread_agents !== 0 ?
                                    <span>{unread_agents}</span> :
                                    ''
                                }
                            </button>
                        </div>
                        <div className='user-list-group'>
                            {this.state.selectedUsersGroup === 0 ?
                                this.renderUsersGroup(users.get('candidates'), 'team network') :
                                this.renderUsersGroup(users.get('agents'), 'agents')}
                        </div>
                    </div>
                </Scrollbars>
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        users: state.get('users')
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
