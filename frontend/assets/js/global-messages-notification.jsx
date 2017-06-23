import React from 'react';
import { connect } from 'react-redux';


class GlobalMessagesNotification extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            originalTitle: document.title
        }
    }

    render() {
        const unread_candidates = this.props.chats.get('candidates').reduce((result, chat) => result + chat.get('unread'), 0);
        const unread_agents = this.props.chats.get('agents').reduce((result, chat) => result + chat.get('unread'), 0);
        const unread_groups = this.props.chats.get('groups').reduce((result, chat) => result + chat.get('unread'), 0);
        const unread_sum = unread_candidates + unread_agents + unread_groups
        if (unread_sum > 0) {
            document.title = `[${unread_sum}] ${this.state.originalTitle}`;
            return (
                <span style={{
                    borderRadius: 3,
                    width: 20,
                    height: 20,
                    backgroundColor: '#37a000',
                    color: 'white',
                    fontWeight: 700,
                    textAlign: 'center'}}
                >
                    {unread_sum}
                </span>
            );
        } else {
            document.title = this.state.originalTitle;
            return <div />;
        }
    }
}

function mapStateToProps (state) {
    return {
        chats: state.get('chats')
    };
}

export default connect(
    mapStateToProps
)(GlobalMessagesNotification);
