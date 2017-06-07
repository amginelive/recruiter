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

export function initChat(user_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.initChat, {user_id});
    }
}

export function moreMessages(message_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.moreMessages, {message_id});
    }
}

export function userIdle() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userIdle, {});
    }
}

export function userActive() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userActive, {});
    }
}
