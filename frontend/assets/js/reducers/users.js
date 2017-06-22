import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

function sortUsersMap(map) {
    ['candidates', 'agents', 'groups'].forEach(group => {
        map = map.update(group, conversations => {
            return conversations.sortBy(conversation => new Date(conversation.get('last_message_time')), (a, b) => a === b ? 0 : (a > b ? -1 : 1));
        });
    });
    return map;
}

const users = (state = new Immutable.Map().withMutations(ctx => ctx.set('self', 0).set('activeChat', 0).set('agents', new Immutable.OrderedMap()).set('candidates', new Immutable.OrderedMap()).set('groups', new Immutable.OrderedMap())), action) => {
    if (action.type === messageTypes.initUsers) {
        state = Immutable.OrderedMap(Immutable.fromJS(action.payload));
        return sortUsersMap(state);
    }
    //if (action.type === messageTypes.userPresence) { // TODO: rework this, this is a map of groups of maps of user ids.
    //    return state.mergeDeep(action.payload);
    //}
    if (action.type === messageTypes.initChat) {
        return state.set('activeChat', action.payload.conversation_id);
    }
    if (action.type === messageTypes.userTyping) {
        if (state.get('agents').has(action.payload.id.toString())) {
            return state.mergeIn(['agents', action.payload.conversation_id.toString()], {online: 2});
        } else if (state.get('candidates').has(action.payload.conversation_id.toString())) {
            return state.mergeIn(['candidates', action.payload.conversation_id.toString()], {online: 2});
        } else return state;
    }
    if (action.type === messageTypes.newMessage) {
        if (action.payload.conversation_id !== state.get('activeChat')) {
            ['candidates', 'agents'].forEach(group => {
                if (state.get(group).has(action.payload.conversation_id.toString())) {
                    state = sortUsersMap(state.mergeIn(
                        [group, action.payload.conversation_id.toString()],
                        {
                            unread: state.getIn([group, action.payload.conversation_id.toString(), 'unread']) + 1
                        }
                    ));
                }
            });
        }

        ['candidates', 'agents'].forEach(group => {
            if (state.get(group).has(action.payload.conversation_id.toString())) {
                state = sortUsersMap(state.mergeIn(
                    [group, action.payload.conversation_id.toString()],
                    {
                        last_message_text: (action.payload.user.id === state.get('self') ? 'You: ' : `${action.payload.user.name}: `) + action.payload.text,
                        last_message_time: action.payload.time
                    }
                ));
            }
        });

        if (state.get('agents').has(action.payload.conversation_id.toString())) {
            return state.mergeIn(['agents', action.payload.conversation_id.toString()], {online: 2});
        } else if (state.get('candidates').has(action.payload.conversation_id.toString())) {
            return state.mergeIn(['candidates', action.payload.conversation_id.toString()], {online: 2});
        } else return state;
    }
    if (action.type === messageTypes.readMessage) {
        if (state.get('agents').has(action.payload.toString())) {
            return state.mergeIn(['agents', action.payload.toString()], {unread: 0});
        } else if (state.get('candidates').has(action.payload.toString())) {
            return state.mergeIn(['candidates', action.payload.toString()], {unread: 0});
        } else return state;
    }
    if (action.type === messageTypes.createGroup) {
        const {id, ...payload} = action.payload;
        return sortUsersMap(state.setIn(['groups', id.toString()], Immutable.fromJS(payload)));
    }
    return state;
};

export {
    users
};
