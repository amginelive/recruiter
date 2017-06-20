const host = window.location.host;

// makes an object of the form {userJoined: 'userJoined'}
const messageTypes = [
    'initChat',
    'initUsers',
    'userPresence',
    'newMessage',
    'moreMessages',
    'userTyping',
    'userIdle',
    'readMessage',
    'createGroup'
].reduce((accum, msg) => {
    accum[ msg ] = msg;
    return accum;
}, {});

const ws_schema = window.location.protocol === 'https:' ? 'wss' : 'ws';
const uri = `${ws_schema}://${host}/chat/${window.location.pathname === '/chat/' ? '' : 'bg'}`;

export {
    host,
    messageTypes,
    uri
};
