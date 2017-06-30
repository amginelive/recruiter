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
                let href = links[i-1];
                if (!href.startsWith('http://') && !href.startsWith('https://')) {
                    href = `http://${href}`;
                }
                result.push(<a key={i} href={href} target='_blank'>{links[i-1]}</a>);
                result.push(splits[i]);
            }
        }
        return result;
    } else return message;
}

const Message = props => {
    return (
        <div className='message-list-item'>
            {}
            <div className={'user-avatar' + (props.user.get('online') === 2 ? ' user-online' : (props.user.get('online') === 1 ? ' user-away': ''))}>
                <img src={props.user.get('photo')} />
            </div>
            <div className='message-list-item-body'>
                <div className='message-list-item-header'>
                    <span className='message-list-item-name'>{props.user.get('name')}</span>
                    <span className='message-list-item-time'>{moment(props.time, moment.ISO_8601).format('h:mm a')}</span>
                </div>
                <p className='message-list-item-text'>{formatLinks(props.text)}</p>
                {props.group_invite && props.group_invite.get('status') === 1 ? <div className='message-list-item-event'><button onClick={() => props.onAccept(props.group_invite.get('conversation_id'), props.group_invite.get('invite_id'))} className='chat-button'>Accept</button><button onClick={() => props.onDecline(props.group_invite.get('conversation_id'), props.group_invite.get('invite_id'))} className='chat-button'>Decline</button></div> : ''}
                {props.group_invite && props.group_invite.get('status') === 2 ? <div className='message-list-item-event'>Declined invitation</div> : ''}
                {props.group_invite && props.group_invite.get('status') === 0 ? <div className='message-list-item-event'>Accepted invitation</div> : ''}
            </div>
        </div>
    );
};

export default Message;
