import React from 'react';

const Message = props => {
    return (
        <div className='message-list-item'>
            <span className='message-list-item-name'>{props.user.name}</span>
            <p className='message-list-item-text'>{props.text}</p>
            <span className='message-list-item-time'>{props.time}</span>
        </div>
    );
};

export default Message;
