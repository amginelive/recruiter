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

        const merged_users = users.merge(users.get('extra')).delete('extra').delete('self');
        let UI = <div />;
        if (chats.get('groups').get(chats.get('activeChat').toString())) {
            const participants = chats.get('groups').get(chats.get('activeChat').toString()).get('users');
            UI = (
                <div className='chat-header'>
                    <div className='chat-header-names'>
                        {participants.mapEntries((entry, index) => {
                            return [index, <span key={entry[0]}>{merged_users.get(entry[0].toString()).get('name') + (index + 1 !== participants.size ? ', ' : '')}</span>]
                        }).toArray()}
                    </div>
                    <div className='chat-header-actions'>
                        <span className='glyphicon glyphicon-user' onClick={this.props.infoGroupModal}></span>
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
