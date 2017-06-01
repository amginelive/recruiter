import {messageTypes, uri} from '../config.js';

class ChatSocket {
    constructor() {
        this.listenMap = new Map();
        this.attempts = 1;
    }

    emit(type, payload) {
        if (this.websocket.readyState > 1) {
            this.websocket.onerror(null);
        } else {
            this.websocket.send(JSON.stringify({type, payload}));
        }
    }

    on(type, callback) {
        this.listenMap.set(type, callback);
    }

    createWebSocket() {
        this.websocket = new WebSocket(uri);

        this.websocket.onopen = () => {
            this.attempts = 1;
        };

        this.websocket.onmessage = event => {
            const data = JSON.parse(event.data);
            const callback = this.listenMap[data.type];
            if (callback) {
                callback(data.payload);
            }
        };

        function generateInterval (k) {
            return Math.min(30, (Math.pow(2, k) - 1)) * 1000;
        }
        this.websocket.onclose = () => {
            const time = generateInterval(this.attempts);

            setTimeout(() => {
                // We've tried to reconnect so increment the attempts by 1
                this.attempts++;

                // Connection has closed so try to reconnect every 10 seconds.
                this.createWebSocket();
            }, time);
        }
    }
}

const socket = new ChatSocket();
window.socket = socket;

const init = (store) => {
    // add listeners to socket messages so we can re-dispatch them as actions
    socket.createWebSocket();
    Object.keys(messageTypes)
        .forEach(type => socket.on(type, (payload) => store.dispatch({ type, payload })));
};

const emit = (type, payload) => socket.emit(type, payload);

export {
    init,
    emit
};
