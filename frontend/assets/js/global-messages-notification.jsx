import React from 'react';
import { connect } from 'react-redux';


class GlobalMessagesNotification extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const unread_candidates = this.props.users.get('candidates').reduce((result, user) => result + user.get('unread'), 0);
        const unread_agents = this.props.users.get('agents').reduce((result, user) => result + user.get('unread'), 0);
        if (unread_candidates + unread_agents > 0) {
            return (
                <span>
                    {unread_candidates + unread_agents}
                </span>
            );
        } else return <div />;
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
