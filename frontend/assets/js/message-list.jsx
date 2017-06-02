import React from 'react';
import { connect } from 'react-redux';
import { Scrollbars } from 'react-custom-scrollbars';

import Message from './message.jsx';


class MessageList extends React.Component {
    constructor(props) {
        super(props);

        this.scrollList = this.scrollList.bind(this);
    }

    scrollList(value) {
        this.scroll.scrollTop(value);
    }

    componentDidUpdate() {
        setTimeout(
            () => {
                this.scrollList(this.scroll.getScrollHeight());
            },
            10
        );
    }

    render() {
        const { messages } = this.props;
        return (
            <div className='message-list-container'>
                <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                            style={{height: 500 + 'px'}}
                            autoHide autoHideTimeout={1000}
                            autoHideDuration={200}>
                    <div className='message-list'>
                        {messages.get('messageList').map((message, index) => {
                            return <Message key={index} user={message.get('user')} text={message.get('text')} time={message.get('time')}/>;
                        }).toArray()}
                    </div>
                </Scrollbars>
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        messages: state.get('messages')
    };
}

export default connect(
    mapStateToProps
)(MessageList);
