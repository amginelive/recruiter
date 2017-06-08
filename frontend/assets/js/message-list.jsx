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
            prevScrollHeight: 0,
        };
    }

    scrollList(value) {
        this.scroll.scrollTop(value);
    }

    componentDidUpdate(prevProps, prevState) { // This is keeping scroll in place on requesting more messages.
        if (prevProps.messages.get('messageList').size !== 0 && (this.props.messages.get('messageList').size - prevProps.messages.get('messageList').size > 1)) {
            this.scrollList(this.scroll.getScrollHeight() - this.state.prevScrollHeight);
        }
    }

    componentWillReceiveProps(nextProps) {
        const { messages } = nextProps;

        const {scrollTop, clientHeight, scrollHeight} = this.scroll.getValues();
        if ((scrollTop + clientHeight === scrollHeight) && // We are at the bottom of scroll list
            ((messages.get('messageList').size - this.props.messages.get('messageList').size === 1) || // One new message
                (this.props.messages.get('messageList').size === 0 && // Or chat init
                messages.get('messageList').size - this.props.messages.get('messageList').size >= 1))) {
            setTimeout(
                () => {
                    this.scrollList(this.scroll.getScrollHeight());
                },
                10
            );
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
        this.setState({prevScrollHeight: this.scroll.getScrollHeight()});
        this.props.actions.moreMessages(first_message_id);
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
                        {messages.get('more') ? <button onClick={this.moreMessages.bind(this, messages.get('messageList').get(0).get('id'))}>More</button> : ''}
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
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        messages: state.get('messages')
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
