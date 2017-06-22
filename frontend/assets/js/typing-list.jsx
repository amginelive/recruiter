import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import * as actions from './actions/index.js';


class TypingList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            userTypingExpireTime: 3
        }
    }

    componentWillReceiveProps(nextProps) {
        const { typing } = nextProps;
        typing.get('typingMap').entrySeq().forEach(entry => {
            if (entry[1].get('timer_id') === 0) {
                const timer_id = setTimeout(() => {
                    this.props.actions.typeTimerExpire({
                        user_id: entry[0],
                        user_name: entry[1].get('user_name'),
                        timer_id
                    });
                }, this.state.userTypingExpireTime*1000);
                this.props.actions.typeTimerStart({
                    user_id: entry[0],
                    user_name: entry[1].get('user_name'),
                    timer_id
                });
            }
        });
    }

    render() {
        const { typing } = this.props;
        return (
            <div className='user-type-list'>
                {typing.get('typingMap').map((user, index) => {
                    return <div key={index} className='user-type-list-item'>{user.get('user_name') + ' is typing...'}</div> // TODO: obviously we want one string here.
                }).toArray()}
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
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
)(TypingList);
