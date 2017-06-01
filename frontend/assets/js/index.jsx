import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import Immutable from 'immutable';
import { createStore, applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import 'whatwg-fetch';
import 'es6-promise/auto';
import { AppContainer } from 'react-hot-loader';

import App from './chat.jsx';
import rootReducer from './reducers/index.js';
import { init as websocketInit, emit } from './actions/websocket.js';


const initialState = new Immutable.Map();

function startUp () {
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

    return store;
}


const container = document.getElementById('app');

const render = (Component) => {
    ReactDOM.render(
        <AppContainer>
            <Provider store={startUp()}>
                <Component />
            </Provider>
        </AppContainer>,
        container
    );
};

render(App);

if (module.hot) {
    module.hot.accept('./chat.jsx', () => {
        ReactDOM.unmountComponentAtNode(container);
        render(App);
    });
}
