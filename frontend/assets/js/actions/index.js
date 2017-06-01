import * as config from '../config.js';
import * as actionTypes from './action-types.js';


const { messageTypes } = config;

export function sendMessage(message) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.newMessage, { message });
    }
}

export function userTyping() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userTyping, {});
    }
}

export function initUserList(userList) {
    return {type: actionTypes.userListInit, payload: userList};
}
