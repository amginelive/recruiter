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

    createWebSocket(that) {
        this.websocket = new WebSocket(uri);

        this.websocket.onopen = () => {
            that.attempts = 1;
        };

        this.websocket.onmessage = event => {
            const data = JSON.parse(event.data);
            const callback = that.listenMap.get(data.type);
            if (callback) {
                callback(data.payload);
            }
        };

        function generateInterval (k) {
            return Math.min(30, (Math.pow(2, k) - 1)) * 1000;
        }
        this.websocket.onclose = () => { // TODO: stop reconnecting attempts on legit server decline.
            const time = generateInterval(that.attempts);

            setTimeout(() => {
                // We've tried to reconnect so increment the attempts by 1
                that.attempts++;

                // Connection has closed so try to reconnect every 10 seconds.
                that.createWebSocket(that);
            }, time);
        }
    }
}

const socket = new ChatSocket();
window.socket = socket;

const init = (store) => {
    // add listeners to socket messages so we can re-dispatch them as actions
    socket.createWebSocket(socket);
    Object.keys(messageTypes)
        .forEach(type => socket.on(type, (payload) => store.dispatch({ type, payload })));
};

const emit = (type, payload) => socket.emit(type, payload);

export {
    init,
    emit
};
