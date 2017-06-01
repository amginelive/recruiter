import Immutable from 'immutable';

import * as config from '../config.js';
import * as actionTypes from '../actions/action-types.js';


const { messageTypes } = config;

const typing = (state = new Immutable.Set(), action) => {
    if (action.type === messageTypes.userTyping) {
        return state.add(Immutable.fromJS({
            user: action.payload,
            timer_id: 0
        }));
    }
    if (action.type === actionTypes.typeTimerStart) {
        return state.add(Immutable.fromJS({
            user: action.payload.user,
            timer_id: action.payload.timer_id
        }));
    }
    if (action.type === actionTypes.typeTimerExpire) {
        value = state.get(action.payload.user);
        if (value && value.timer_id === action.payload.timer_id) {
            return state.delete(value);
        } else {
            return state;
        }
    }
    return state;
};

export {
    typing
};
