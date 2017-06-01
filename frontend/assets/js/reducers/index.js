import { combineReducers } from 'redux-immutable'

import { messages } from './messages.js';
import { typing } from './typing.js';

export default combineReducers({
    messages,
    typing
});
