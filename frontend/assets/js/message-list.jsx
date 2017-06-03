import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Scrollbars } from 'react-custom-scrollbars';

import * as actions from './actions/index.js';
import Message from './message.jsx';


class MessageList extends React.Component {
    constructor(props) {
        super(props);

        this.scrollList = this.scrollList.bind(this);
        this.state = {
            userTypingExpireTime: 3
        };
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

    componentWillReceiveProps(nextProps) {
        const { typing } = nextProps;
        if (typing.size === 0) {
            return;
        }
        typing.get('typingMap').entrySeq().forEach(entry => {
            if (entry[1].get('timer_id') === 0) {
                const timer_id = setTimeout(() => {
                    this.props.actions.typeTimerExpire({
                        user_id: entry[0],
                        user_name: entry[1].get('user_name'),
                        timer_id
                    });
                }, this.state.userTypingExpireTime*1000);
                this.props.actions.typeTimerStart({
                    user_id: entry[0],
                    user_name: entry[1].get('user_name'),
                    timer_id
                });
            }
        });
    }

    render() {
        const { messages, typing } = this.props;
        let typingUI = (<div></div>);
        if (typing.size > 0) {
            typingUI = (
                <div className='user-type-list'>
                    {typing.get('typingMap').map((user, index) => {
                        return <div key={index} className='user-type-list-item'>{user.get('user_name') + ' is typing...'}</div>
                    }).toArray()}
                </div>
            );
        }
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
                {typingUI}
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        messages: state.get('messages'),
        typing: state.get('typing')
    };
}

function mapDispatchToProps (dispatch) {
    return {
        dispatch: dispatch,
        actions: bindActionCreators(actions, dispatch)
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(MessageList);
