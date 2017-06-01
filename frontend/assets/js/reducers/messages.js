import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

const messages = (state = new Immutable.List(), action) => {
    if (action.type === messageTypes.initChat) {
        return Immutable.fromJS(action.payload);
    }
    if (action.type === messageTypes.newMessage) {
        return state.push(Immutable.fromJS(action.payload));
    }
    return state;
};

export {
    messages
};
