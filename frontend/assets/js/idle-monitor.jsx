import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import IdleTimer from 'react-idle-timer';

import * as actions from './actions/index.js';


class IdleMonitor extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            timeout: 60
        }
    }

    render() {
        return <IdleTimer
            element={document}
            activeAction={this.props.actions.userActive}
            idleAction={this.props.actions.userIdle}
            timeout={this.state.timeout*1000} />;
    }
}

function mapStateToProps (state) {
    return {};
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
)(IdleMonitor);
