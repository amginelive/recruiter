import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Scrollbars } from 'react-custom-scrollbars';
import moment from 'moment';

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

    formatDate(date) {
        const now = moment();
        const then = moment(date);
        if (then.isSame(now, 'day')) {
            return 'Today';
        } else if (then.isSame(now.subtract(1, 'days'), 'day')) {
            return 'Yesterday';
        } else if (then.isBetween(now.subtract(5, 'days'), now, 'day')) {
            return then.format('dddd');
        } else {
            return then.format('dddd, MMMM Do, YYYY');
        }
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
                            let dateUI = '';
                            if (index === 0 || !moment(message.get('time')).isSame(moment(messages.get('messageList').get(index-1).get('time')), 'day')) {
                                dateUI = <div className='message-list-date'>{this.formatDate(message.get('time'))}</div>
                            }
                            return (
                                <div key={index}>
                                    {dateUI}
                                    <Message user={message.get('user')} text={message.get('text')} time={message.get('time')}/>
                                </div>
                            );
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
