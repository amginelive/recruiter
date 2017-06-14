import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

function sortUsersMap(map) {
    ['candidates', 'agents'].forEach(group => {
        map = map.update(group, users => {
            return users.sortBy(user => new Date(user.get('last_message_time')), (a, b) => a === b ? 0 : (a > b ? -1 : 1));
        });
    });
    return map;
}

const users = (state = new Immutable.OrderedMap().withMutations(ctx => ctx.set('self', 0).set('activeChat', 0).set('agents', new Immutable.Map()).set('candidates', new Immutable.Map())), action) => {
    if (action.type === messageTypes.initUsers) {
        state = Immutable.OrderedMap(Immutable.fromJS(action.payload));
        return sortUsersMap(state);
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
            ['candidates', 'agents'].forEach(group => {
                if (state.get(group).has(action.payload.user.id.toString())) {
                    state = sortUsersMap(state.mergeIn(
                        [group, action.payload.user.id.toString()],
                        {
                            unread: state.getIn([group, action.payload.user.id.toString(), 'unread']) + 1
                        }
                    ));
                }
            });
        }

        ['candidates', 'agents'].forEach(group => {
            if (state.get(group).has(action.payload.user.id.toString())) {
                state = sortUsersMap(state.mergeIn(
                    [group, action.payload.user.id.toString()],
                    {
                        last_message_text: (action.payload.user.id === state.get('self') ? 'You: ' : `${action.payload.user.name}: `) + action.payload.text,
                        last_message_time: action.payload.time
                    }
                ));
            }
        });
        if (state.get('self') === action.payload.user.id) {
            ['candidates', 'agents'].forEach(group => {
                const result = state.get(group).findEntry(value => value.get('conversation_id') === action.payload.conversation_id);
                if (result) {
                    state = sortUsersMap(state.mergeIn(
                        [group, result[0]],
                        {
                            last_message_text: `You: ${action.payload.text}`,
                            last_message_time: action.payload.time
                        }
                    ));
                }
            });
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
