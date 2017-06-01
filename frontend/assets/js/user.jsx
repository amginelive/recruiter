import React from 'react';

const User = props => {
    return (
        <div onClick={() => {props.onUserInit(props.id)}} className='user-list-item'>
            <span className='user-list-item-name'>{props.name}</span>
        </div>
    );
};

export default User;
