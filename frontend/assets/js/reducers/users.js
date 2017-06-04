import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

const users = (state = new Immutable.List(), action) => {
    if (action.type === messageTypes.initUsers) {
        return Immutable.fromJS(action.payload);
    }
    if (action.type === messageTypes.userPresence) {
        return state.mergeDeep(action.payload)
    }
    if (action.type === messageTypes.userTyping) {
        return state.update(
            state.findIndex(item => {return item.get('id') === action.payload.id}),
            item => item.set('online', true)
        );
    }
    if (action.type === messageTypes.newMessage) {
        return state.update(
            state.findIndex(item => {return item.get('id') === action.payload.user.id}),
            item => item.set('online', true)
        );
    }
    return state;
};

export {
    users
};
