import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

const users = (state = new Immutable.Map().withMutations(ctx => ctx.set('activeChat', 0).set('agents', new Immutable.Map()).set('candidates', new Immutable.Map())), action) => {
    if (action.type === messageTypes.initUsers) {
        return Immutable.fromJS(action.payload);
    }
    if (action.type === messageTypes.userPresence) {
        return state.mergeDeep(action.payload);
    }
    if (action.type === messageTypes.initChat) {
        return state.set('activeChat', action.payload.conversation_id);
    }
    if (action.type === messageTypes.userTyping) {
        if (state.get('agents').has(action.payload.id.toString())) {
            return state.mergeIn(['agents', action.payload.id.toString()], {online: 2});
        } else if (state.get('candidates').has(action.payload.id.toString())) {
            return state.mergeIn(['candidates', action.payload.id.toString()], {online: 2});
        } else return state;
    }
    if (action.type === messageTypes.newMessage) {
        if (action.payload.conversation_id !== state.get('activeChat')) {
            if (state.get('agents').has(action.payload.user.id.toString())) {
                state = state.mergeIn(['agents', action.payload.user.id.toString()], {unread: state.getIn(['agents', action.payload.user.id.toString(), 'unread'])+1});
            } else if (state.get('candidates').has(action.payload.user.id.toString())) {
                state = state.mergeIn(['candidates', action.payload.user.id.toString()], {unread: state.getIn(['candidates', action.payload.user.id.toString(), 'unread'])+1});
            }
        }
        if (state.get('agents').has(action.payload.user.id.toString())) {
            return state.mergeIn(['agents', action.payload.user.id.toString()], {online: 2});
        } else if (state.get('candidates').has(action.payload.user.id.toString())) {
            return state.mergeIn(['candidates', action.payload.user.id.toString()], {online: 2});
        } else return state;
    }
    if (action.type === messageTypes.readMessage) {
        if (state.get('agents').has(action.payload.toString())) {
            return state.mergeIn(['agents', action.payload.toString()], {unread: 0});
        } else if (state.get('candidates').has(action.payload.toString())) {
            return state.mergeIn(['candidates', action.payload.toString()], {unread: 0});
        } else return state;
    }
    return state;
};

export {
    users
};
