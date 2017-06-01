import * as config from '../config.js';


const { messageTypes } = config;

export function sendMessage (message) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.newMessage, { message });
    }
}

export function userTyping () {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userTyping, {});
    }
}
