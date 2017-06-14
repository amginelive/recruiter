import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Scrollbars } from 'react-custom-scrollbars';
import moment from 'moment';
import { Loader } from 'react-loaders';

import * as actions from './actions/index.js';
import Message from './message.jsx';


class MessageList extends React.Component {
    constructor(props) {
        super(props);

        this.scrollList = this.scrollList.bind(this);
        this.state = {
            prevScrollHeight: 0,
            pendingMore: false
        };
    }

    scrollList(value) {
        this.scroll.scrollTop(value);
    }

    componentDidUpdate(prevProps, prevState) { // This is keeping scroll in place on requesting more messages.
        if (!this.scroll) {
            return;
        }
        if (prevProps.messages.get('messageList').size !== 0 && (this.props.messages.get('messageList').size - prevProps.messages.get('messageList').size > 1)) {
            this.scrollList(this.scroll.getScrollHeight() - this.state.prevScrollHeight);
        }
    }

    componentWillReceiveProps(nextProps) {
        const { messages } = nextProps;

        if (messages.get('more') === this.props.messages.get('more') && messages.get('messageList').size - this.props.messages.get('messageList').size === 1) { // One new message came
            this.props.actions.readMessage(messages.get('messageList').last().get('id'));
            setTimeout(() => this.scrollList(this.scroll.getScrollHeight()), 10);
        }
        if (this.props.messages.get('activeChat') !== messages.get('activeChat')) { // Chat init happened
            this.props.setChatInitPendingState(false);
            setTimeout(() => this.scrollList(this.scroll.getScrollHeight()), 10);
        }
        if (this.props.messages.get('activeChat') === messages.get('activeChat')
            && (messages.get('messageList').size - this.props.messages.get('messageList').size > 1
                || (messages.get('messageList').size - this.props.messages.get('messageList').size === 1
                && messages.get('more') !== this.props.messages.get('more')))) { // More messages loaded
            this.setState({pendingMore: false});
        }
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

    moreMessages(first_message_id) {
        this.setState({
            prevScrollHeight: this.scroll.getScrollHeight(),
            pendingMore: true
        });
        this.props.actions.moreMessages(first_message_id);
    }

    renderMoreMessagesButton(messages) {
        if (this.state.pendingMore) {
            return <Loader type='ball-pulse' active />
        } else if (messages.get('more')) {
            return <button onClick={this.moreMessages.bind(this, messages.get('messageList').get(0).get('id'))}>More</button>;
        } else {
            return <div />;
        }
    }

    render() {
        const { messages, users, chatInitPending } = this.props;

        if (chatInitPending) {
            return (
                <div className='message-list-container'>
                    <Loader type='ball-pulse' active />
                </div>
            );
        }

        const moreMessagesButtonUI = this.renderMoreMessagesButton(messages);
        return (
            <div className='message-list-container'>
                <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                            style={{height: '100%'}}
                            autoHide autoHideTimeout={1000}
                            autoHideDuration={200}>
                    <div className='message-list'>
                        {moreMessagesButtonUI}
                        {messages.get('messageList').map((message, index) => {
                            let dateUI = '';
                            if (index === 0 || !moment(message.get('time')).isSame(moment(messages.get('messageList').get(index-1).get('time')), 'day')) {
                                dateUI = <div className='message-list-date'>{this.formatDate(message.get('time'))}</div>
                            }
                            return (
                                <div key={index}>
                                    {dateUI}
                                    <Message user={message.get('user').get('id') === users.get('self') ? message.get('user').set('online', 2) : users.get(message.get('user').get('type')).get(message.get('user').get('id').toString())} text={message.get('text')} time={message.get('time')}/>
                                </div>
                            );
                        }).toArray()}
                    </div>
                </Scrollbars>
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        messages: state.get('messages'),
        users: state.get('users')
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
