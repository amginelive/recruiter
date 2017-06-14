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
            activeUser: 0,
            userPresencePollingInterval: 10,
            selectedUsersGroup: 0
        };
        setInterval(() => this.props.actions.userPresence(), this.state.userPresencePollingInterval*1000);
    }

    componentDidUpdate(prevProps, prevState) {
        /*if (this.props.users.size > 0 && this.state.activeUser === 0) {
            this.setState({activeUser: this.props.users.toArray()[0].get('id')});
        }*/
    }

    userInit(id) {
        if (id === this.state.activeUser) {
            return;
        }
        this.props.setChatInitPendingState(true);
        this.props.actions.initChat(id);
        this.setState({activeUser: id});
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
        return users.entrySeq().map(entry => {
            const show_last_message = moment(entry[1].get('last_message_time')).valueOf() > 60*60*24;
            return (
                <div
                    onClick={() => {this.userInit(entry[0])}}
                    key={entry[0]}
                    className={'user-list-item' + (entry[0] === this.state.activeUser ? ' active' : '')}
                >
                    <div className={'user-avatar' + (entry[1].get('online') === 2 ? ' user-online' : (entry[1].get('online') === 1 ? ' user-away': ''))}>
                        <img src={entry[1].get('photo')} />
                    </div>
                    <div className='user-list-item-pane'>
                        <div className='user-list-item-pane-header'>
                            <span className='user-list-item-name'>{entry[1].get('name')}</span>
                            {show_last_message ? <span className='user-list-item-timestamp'>{this.formatDate(entry[1].get('last_message_time'))}</span> : ''}
                        </div>
                        {show_last_message ? <span className='user-list-item-message'>{entry[1].get('last_message_text')}</span> : ''}
                    </div>
                    {entry[1].get('unread') > 0 ? <div className='user-list-item-unread'><span>{entry[1].get('unread')}</span></div> : ''}
                </div>
            );
        }).toArray();
    }

    handleUserGroupSelect(group) {
        this.setState({selectedUsersGroup: group});
    }

    render() {
        const { users } = this.props;
        return (
            <div className='user-list-container'>
                <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                                style={{height: '100%'}}
                                autoHide autoHideTimeout={1000}
                                autoHideDuration={200}>
                    <div className='user-list'>
                        <div className='user-list-header'>
                            <button className={'chat-button user-list-button button-candidates' + (this.state.selectedUsersGroup === 0 ? ' active' : '')} onClick={this.handleUserGroupSelect.bind(this, 0)}>Candidates</button>
                            <button className={'chat-button user-list-button button-agents' + (this.state.selectedUsersGroup === 1 ? ' active' : '')} onClick={this.handleUserGroupSelect.bind(this, 1)}>Agents</button>
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
