import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Scrollbars } from 'react-custom-scrollbars';

import * as actions from './actions/index.js';


class UserList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            activeUser: 0
        };
    }

    componentDidMount() {
        fetch('/chat/users/', {
            credentials: 'same-origin'
        }).then(response => response.json()).then(json => {
            this.props.actions.initUserList(json);
        });
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

    render() {
        const { users } = this.props;
        return (
            <div className='user-list-container'>
                <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                                style={{height: 500 + 'px'}}
                                autoHide autoHideTimeout={1000}
                                autoHideDuration={200}>
                    <div className='user-list'>
                        {users.map(user => {
                            return (
                                <div
                                    onClick={() => {this.userInit(user.get('id'))}}
                                    key={user.get('id')}
                                    name={user.get('name')}
                                    id={user.get('id')}
                                    className={'user-list-item' + (user.get('id') === this.state.activeUser ? ' active-user' : '')}
                                >
                                    <span className='user-list-item-name'>{user.get('name')}</span>
                                </div>
                            )
                        }).toArray()}
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
