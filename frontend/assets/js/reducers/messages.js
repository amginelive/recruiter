import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

const messages = (state = new Immutable.Map().withMutations(ctx => ctx.set('activeChat', 0).set('messageList', new Immutable.List())), action) => {
    if (action.type === messageTypes.initChat) {
        return new Immutable.Map().withMutations(ctx => ctx.set('activeChat', action.payload['conversation_id']).set('messageList', Immutable.fromJS(action.payload['messages'])));
    }
    if (action.type === messageTypes.newMessage && action.payload['conversation_id'] === state.get('activeChat')) {
        // TODO: There may be an optimization here, consult Immutable.JS docs
        const messageList = state.get('messageList').push(Immutable.fromJS(action.payload));
        return state.set('messageList', messageList);
    }
    return state;
};

export {
    messages
};
