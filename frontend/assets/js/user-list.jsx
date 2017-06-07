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
                    <span className={'user-list-item-status' + (user.get('online') === true ? ' user-online' : '')}>●</span>
                    <span className='user-list-item-name'>{user.get('name')}</span>
                </div>
            );
        }).toArray();
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
                        <div className='user-list-group'>
                            <div className='user-list-group-header'>My team network</div>
                            {this.renderUsersGroup(users.get('candidates'), 'team network')}
                        </div>
                        <div className='user-list-group'>
                            <div className='user-list-group-header'>Agents</div>
                            {this.renderUsersGroup(users.get('agents'), 'agents')}
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
