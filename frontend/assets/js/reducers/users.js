import Immutable from 'immutable';

import * as actionTypes from '../actions/action-types.js';


const users = (state = new Immutable.List(), action) => {
    if (action.type === actionTypes.userListInit) {
        return Immutable.fromJS(action.payload);
    }
    return state;
};

export {
    users
};
