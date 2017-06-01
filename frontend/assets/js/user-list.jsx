import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from './actions/index.js';


class UserList extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        fetch('/chat/users/', {
            credentials: 'same-origin'
        }).then(response => response.json()).then(json => {
            console.log(json);
            this.props.actions.initUserList(json);
        });
    }

    render() {
        const { users } = this.props;
        return (
            <div className='user-list'>
                {users.map(user => {
                    return (
                        <div key={user.get('id')} className='user-list-item'>
                            <span className='user-list-item-name'>{user.get('name')}</span>
                        </div>
                    );
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
