import React from 'react';
import { connect } from 'react-redux';

import Message from './message.jsx';


class MessageList extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const { messages } = this.props;
        return (
            <div className='message-list'>
                {messages.get('messageList').map((message, index) => {
                    return <Message key={index} user={message.get('user')} text={message.get('text')} time={message.get('time')}/>;
                }).toArray()}
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        messages: state.get('messages')
    };
}

export default connect(
    mapStateToProps
)(MessageList);
