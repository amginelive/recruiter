import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import Immutable from 'immutable';
import { createStore, applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import { AppContainer } from 'react-hot-loader';

import App from './chat.jsx';
import IdleMonitor from './idle-monitor.jsx';
import rootReducer from './reducers/index.js';
import { init as websocketInit, emit } from './actions/websocket.js';


(function startUp() {
    const thunk = thunkMiddleware.default ? thunkMiddleware.default : thunkMiddleware;
    const middleware = [thunk.withExtraArgument({emit})];

    const setup = applyMiddleware(...middleware)(createStore);

    let store = setup(rootReducer);
    websocketInit(store); // setup websocket listeners etc

    if (module.hot) {
        // Enable Webpack hot module replacement for reducers
        module.hot.accept('./reducers', () => {
            const nextRootReducer = import('./reducers/index.js');
            store.replaceReducer(nextRootReducer);
        });
    }

    window.storeRoot = store;
}());

const render = (Component, container) => {
    ReactDOM.render(
        <AppContainer>
            <Provider store={window.storeRoot}>
                <Component />
            </Provider>
        </AppContainer>,
        container
    );
};

if (window.location.pathname === '/chat/') {
    render(App, document.getElementById('app'));
}

const div = document.createElement('div');
div.id = 'idle-monitor';
document.getElementsByTagName('body')[0].appendChild(div);
render(IdleMonitor, div);

if (module.hot) {
    if (window.location.pathname === '/chat') {
        module.hot.accept('./chat.jsx', () => {
            ReactDOM.unmountComponentAtNode(document.getElementById('app'));
            render(App, document.getElementById('app'));
        });
    }
    module.hot.accept('./idle-monitor.jsx', () => {
        ReactDOM.unmountComponentAtNode(div);
        render(IdleMonitor, div);
    });
}
