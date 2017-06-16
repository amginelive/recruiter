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
        const unread_candidates = this.props.users.get('candidates').reduce((result, user) => result + user.get('unread'), 0);
        const unread_agents = this.props.users.get('agents').reduce((result, user) => result + user.get('unread'), 0);
        if (unread_candidates + unread_agents > 0) {
            document.title = `[${unread_candidates + unread_agents}] ${this.state.originalTitle}`;
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
                    {unread_candidates + unread_agents}
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
        users: state.get('users')
    };
}

export default connect(
    mapStateToProps
)(GlobalMessagesNotification);
