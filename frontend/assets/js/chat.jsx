import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from './actions/index.js';
import UserList from './user-list.jsx';
import MessageList from './message-list.jsx';
import MessageForm from './message-send-form.jsx';


class App extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <UserList />
                <MessageList />
                <MessageForm />
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
