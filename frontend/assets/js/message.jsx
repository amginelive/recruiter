import React from 'react';
import moment from 'moment';
import urlRegex from 'url-regex';

function formatLinks(message) {
    const re = urlRegex({strict: false});
    if (message.search(re) !== -1) {
        const links = message.match(re);
        const splits = message.split(re);
        let result = [];
        for (let i = 0; i < splits.length; i++) {
            if (i === 0) {
                result.push(splits[0]);
            } else {
                result.push(<a key={i} href='#' target='_blank'>{links[i-1]}</a>);
                result.push(splits[i]);
            }
        }
        return result;
    } else return message;
}

const Message = props => {
    return (
        <div className='message-list-item'>
            <div className={'user-avatar' + (props.user.get('online') === 2 ? ' user-online' : (props.user.get('online') === 1 ? ' user-away': ''))}>
                <img src={props.user.get('photo')} />
            </div>
            <div className='message-list-item-body'>
                <div className='message-list-item-header'>
                    <span className='message-list-item-name'>{props.user.get('name')}</span>
                    <span className='message-list-item-time'>{moment(props.time, moment.ISO_8601).format('h:mm a')}</span>
                </div>
                <p className='message-list-item-text'>{formatLinks(props.text)}</p>
            </div>
        </div>
    );
};

export default Message;
