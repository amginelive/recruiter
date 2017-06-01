import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from './actions/index.js';
import User from './user.jsx';


class UserList extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        fetch('/chat/users/', {
            credentials: 'same-origin'
        }).then(response => response.json()).then(json => {
            this.props.actions.initUserList(json);
        });
    }

    userInit(id) {
        this.props.actions.initChat(id);
    }

    render() {
        const { users } = this.props;
        return (
            <div className='user-list'>
                {users.map(user => {
                    return <User key={user.get('id')} name={user.get('name')} id={user.get('id')} onUserInit={this.userInit.bind(this)} />;
                }).toArray()}
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
