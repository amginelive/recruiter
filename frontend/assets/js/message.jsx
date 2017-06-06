import React from 'react';
import moment from 'moment';

const Message = props => {
    return (
        <div className='message-list-item'>
            <img className='message-list-item-photo' src={props.user.get('photo')} />
            <div className='message-list-item-body'>
                <div className='message-list-item-header'>
                    <span className='message-list-item-name'>{props.user.get('name')}</span>
                    <span className='message-list-item-time'>{moment(props.time, moment.ISO_8601).format('h:mm a')}</span>
                </div>
                <p className='message-list-item-text'>{props.text}</p>
            </div>
        </div>
    );
};

export default Message;
