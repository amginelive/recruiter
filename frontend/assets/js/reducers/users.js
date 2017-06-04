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
    return state;
};

export {
    users
};
