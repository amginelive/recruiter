import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

const users = (state = new Immutable.Map().withMutations(ctx => ctx.set('agents', new Immutable.Map()).set('candidates', new Immutable.Map())), action) => {
    if (action.type === messageTypes.initUsers) {
        return Immutable.fromJS(action.payload);
    }
    if (action.type === messageTypes.userPresence) {
        return state.mergeDeep(action.payload)
    }
    if (action.type === messageTypes.userTyping) {
        if (state.get('agents').has(action.payload.id)) {
            return state.mergeIn(['agents', action.payload.id], {online: 2});
        } else {
            return state.mergeIn(['candidates', action.payload.id], {online: 2});
        }
    }
    if (action.type === messageTypes.newMessage) {
        if (state.get('agents').has(action.payload.user.id)) {
            return state.mergeIn(['agents', action.payload.user.id], {online: 2});
        } else {
            return state.mergeIn(['candidates', action.payload.user.id], {online: 2});
        }
    }
    return state;
};

export {
    users
};
