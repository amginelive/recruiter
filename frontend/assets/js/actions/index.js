import * as config from '../config.js';
import * as actionTypes from './action-types.js';


const { messageTypes } = config;

export function sendMessage(message) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.newMessage, message);
    }
}

export function userTyping() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userTyping, {});
    }
}

export function userPresence() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userPresence, {});
    }
}

export function typeTimerStart(payload) {
    return {type: actionTypes.typeTimerStart, payload}
}

export function typeTimerExpire(payload) {
    return {type: actionTypes.typeTimerExpire, payload}
}

export function initChat(conversation_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.initChat, conversation_id);
    }
}

export function moreMessages(message_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.moreMessages, {message_id});
    }
}

export function userIdle(idle) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userIdle, idle);
    }
}

export function readMessage(message_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.readMessage, message_id); // TODO: refactor other actions like this.
    }
}

export function createGroup(payload) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.createGroup, payload);
    }
}

export function answerInvite(payload) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.answerInvite, payload);
    }
}

export function leaveGroup() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.leaveGroup, {});
    }
}

export function kickUser(user_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.kickUser, user_id);
    }
}

export function inviteUser(user_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.inviteUser, user_id);
    }
}
