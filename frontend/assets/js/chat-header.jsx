import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import * as actions from './actions/index.js';


class ChatHeader extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const {users, chats} = this.props;

        let UI = <div />;
        if (chats.get('groups').get(chats.get('activeChat').toString())) {
            const participants = chats.get('groups').get(chats.get('activeChat').toString()).get('users');
            UI = (
                <div className='chat-header'>
                    <div className='chat-header-names'>
                        {participants.map((user_id, index) => {
                            return <span key={user_id}>{users.get(user_id.toString()).get('name') + (index + 1 !== participants.size ? ', ' : '')}</span>
                        })}
                    </div>
                    <div className='chat-header-actions'>
                        <span className='glyphicon glyphicon-user'></span>
                        <span className='glyphicon glyphicon-log-out' onClick={this.props.leaveGroupModal}></span>
                    </div>
                </div>
            )
        }
        return UI;
    }
}

function mapStateToProps (state) {
    return {
        users: state.get('users'),
        chats: state.get('chats')
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
)(ChatHeader);
