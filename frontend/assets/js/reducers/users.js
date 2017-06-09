import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

const users = (state = new Immutable.Map().withMutations(ctx => ctx.set('agents', new Immutable.List()).set('candidates', new Immutable.List())), action) => {
    if (action.type === messageTypes.initUsers) {
        return Immutable.fromJS(action.payload);
    }
    if (action.type === messageTypes.userPresence) {
        return state.mergeDeep(action.payload)
    }
    if (action.type === messageTypes.userTyping) {
        state = state.updateIn(['agents'],
            list => {
                const index = list.findIndex(item => {return item.get('id') === action.payload.id});
                if (index >= 0) {
                    return list.update(index, item => item.set('online', 2));
                } else {
                    return list;
                }
            }
        );
        return state.updateIn(['candidates'],
            list => {
                const index = list.findIndex(item => {return item.get('id') === action.payload.id});
                if (index >= 0) {
                    return list.update(index, item => item.set('online', 2));
                } else {
                    return list;
                }
            }
        );
    }
    if (action.type === messageTypes.newMessage) {
        state = state.updateIn(['agents'],
            list => {
                const index = list.findIndex(item => {return item.get('id') === action.payload.user.id});
                if (index >= 0) {
                    return list.update(index, item => item.set('online', 2));
                } else {
                    return list;
                }
            }
        );
        return state.updateIn(['candidates'],
            list => {
                const index = list.findIndex(item => {return item.get('id') === action.payload.user.id});
                if (index >= 0) {
                    return list.update(index, item => item.set('online', 2));
                } else {
                    return list;
                }
            }
        );
    }
    return state;
};

export {
    users
};
