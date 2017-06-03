import React from 'react';
import moment from 'moment';

const Message = props => {
    return (
        <div className='message-list-item'>
            <div className='message-list-item-header'>
                <span className='message-list-item-name'>{props.user.get('name')}</span>
                <span className='message-list-item-time'>{moment(props.time, moment.ISO_8601).format('h:mm a')}</span>
            </div>
            <p className='message-list-item-text'>{props.text}</p>
        </div>
    );
};

export default Message;
