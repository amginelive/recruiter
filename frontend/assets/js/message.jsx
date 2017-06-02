import React from 'react';
import moment from 'moment';

const Message = props => {
    return (
        <div className='message-list-item'>
            <span className='message-list-item-name'>{props.user.get('name')}</span>
            <p className='message-list-item-text'>{props.text}</p>
            <span className='message-list-item-time'>{moment(props.time, moment.ISO_8601).format('h:mm:ss a')}</span>
        </div>
    );
};

export default Message;
