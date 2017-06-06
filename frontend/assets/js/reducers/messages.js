import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

const messages = (state = new Immutable.Map().withMutations(ctx => ctx.set('activeChat', 0).set('messageList', new Immutable.List())), action) => {
    if (action.type === messageTypes.initChat) {
        return new Immutable.Map().withMutations(ctx => {
            return ctx.set('activeChat', action.payload.conversation_id)
                .set('messageList', Immutable.fromJS(action.payload.messages))
                .set('more', Immutable.fromJS(action.payload.more));
        });
    }
    if (action.type === messageTypes.newMessage && action.payload.conversation_id === state.get('activeChat')) {
        // TODO: There may be an optimization here, consult Immutable.JS docs
        const messageList = state.get('messageList').push(Immutable.fromJS(action.payload));
        return state.set('messageList', messageList);
    }
    if (action.type === messageTypes.moreMessages && action.payload.conversation_id === state.get('activeChat')) {
        const messageList = Immutable.fromJS(action.payload.messages).concat(state.get('messageList'));
        return state.withMutations(ctx => {
            return ctx.set('messageList', messageList)
                .set('more', Immutable.fromJS(action.payload.more));
        });
    }
    return state;
};

export {
    messages
};
