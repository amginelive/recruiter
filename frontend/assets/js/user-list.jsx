import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Scrollbars } from 'react-custom-scrollbars';

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
        if (this.props.users.size > 0 && this.state.activeUser === 0) {
            this.setState({activeUser: this.props.users.toArray()[0].get('id')});
        }
    }

    userInit(id) {
        this.props.actions.initChat(id);
        this.setState({activeUser: id});
    }

    renderUsersGroup(users, group_name) {
        if (users.size === 0) {
            return <div className='empty-user-group'>You have no {group_name} connections</div>
        }
        return users.map(user => {
            return (
                <div
                    onClick={() => {this.userInit(user.get('id'))}}
                    key={user.get('id')}
                    name={user.get('name')}
                    id={user.get('id')}
                    className={'user-list-item' + (user.get('id') === this.state.activeUser ? ' active' : '')}
                >
                    <img className='user-list-item-photo' src={user.get('photo')} />
                    <span className={'user-list-item-status' + (user.get('online') === 2 ? ' user-online' : (user.get('online') === 1 ? ' user-away': ''))}>●</span>
                    <span className='user-list-item-name'>{user.get('name')}</span>
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
                                style={{height: 500 + 'px'}}
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
