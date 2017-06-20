import React from 'react';
import ReactModal from 'react-modal';
import { Scrollbars } from 'react-custom-scrollbars';


class GroupChatModal extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            groupName: '',
            groupMessage: '',
            userSearchQuery: '',
            selectedUsers: [],
            queryUsers: [],
            activeQueryIndex: 0,
            queryUserDOMHeight: 20
        };
    }

    selectUser(index) {
        this.setState({
            selectedUsers: [...this.state.selectedUsers, this.state.queryUsers[index]],
            activeQueryIndex: 0,
            userSearchQuery: '',
            queryUsers: []
        });
    }

    handleKeyPress(event) {
        if (event.key === 'ArrowDown') {
            if (this.state.queryUsers.length > 1) {
                if (this.state.activeQueryIndex < this.state.queryUsers.length - 1) {
                    const scrollValues = this.scroll.getValues();
                    const activeQueryIndex = this.state.activeQueryIndex + 1;
                    const activeElementScroll = this.state.queryUserDOMHeight*(activeQueryIndex + 1);
                    if (activeElementScroll > scrollValues.scrollTop + scrollValues.clientHeight) {
                        this.scroll.scrollTop(scrollValues.scrollTop + this.state.queryUserDOMHeight);
                    }
                    this.setState({activeQueryIndex});
                } else {
                    this.setState({activeQueryIndex: 0});
                    this.scroll.scrollToTop();
                }
            }
            event.preventDefault();
            return;
        }
        if (event.key === 'ArrowUp') {
            if (this.state.queryUsers.length > 1) {
                if (this.state.activeQueryIndex > 0) {
                    const scrollValues = this.scroll.getValues();
                    const activeQueryIndex = this.state.activeQueryIndex - 1;
                    const activeElementScroll = this.state.queryUserDOMHeight*(activeQueryIndex);
                    if (activeElementScroll < scrollValues.scrollTop) {
                        this.scroll.scrollTop(scrollValues.scrollTop - this.state.queryUserDOMHeight);
                    }
                    this.setState({activeQueryIndex});
                } else {
                    this.setState({activeQueryIndex: this.state.queryUsers.length - 1});
                    this.scroll.scrollToBottom();
                }
            }
            event.preventDefault();
            return;
        }
        if (event.key === 'Tab') {
            this.userSearchInput.value = this.state.queryUsers[this.state.activeQueryIndex].name;
            event.preventDefault();
        }
        if (event.key === 'Enter') {
            event.preventDefault();
            if (this.state.queryUsers.length > 0) {
                return this.selectUser(this.state.activeQueryIndex);
            }
        }
        this.searchUsers();
    }

    searchUsers() {
        const users = this.props.users.get('candidates').merge(this.props.users.get('agents'));
        const userSearchQuery = this.userSearchInput.value;
        if (userSearchQuery !== this.state.userSearchQuery) {
            this.setState({userSearchQuery});
            this.setState({activeQueryIndex: 0});
            if (userSearchQuery.length > 0) {
                let queryUsers = users.filter(user => {
                    const has_name = user.get('name').toLowerCase().includes(userSearchQuery.toLowerCase());
                    const has_email = user.get('email').toLowerCase().includes(userSearchQuery.toLowerCase());
                    return has_email || has_name;
                });
                queryUsers = queryUsers.map((user, id) => {
                    return user.set('id', parseInt(id)).toObject();
                }).toArray();
                const selected_ids = this.state.selectedUsers.map(user => user.id);
                queryUsers = queryUsers.filter(user => !selected_ids.some(id => id === user.id));
                this.setState({queryUsers});
            } else {
                this.setState({queryUsers: []});
            }
        }
    }

    removeSelectedUser(index) {
        const {selectedUsers} = this.state;
        selectedUsers.splice(index, 1);
        this.setState(selectedUsers);
    }

    checkGroupMessage() {
        const groupMessage = this.groupMessageInput.value;
        this.setState({groupMessage});
    }

    checkGroupName() {
        const groupName = this.groupNameInput.value;
        this.setState({groupName});
    }

    handleClose() {
        this.setState({
            groupName: '',
            groupMessage: '',
            userSearchQuery: '',
            selectedUsers: [],
            queryUsers: [],
            activeQueryIndex: 0
        });
        this.props.onClose();
    }

    render() {
        let usersQueryUI = '';
        if (this.state.queryUsers.length > 0) {
            const height_max = 60;
            const height = Math.min(this.state.queryUsers.length * this.state.queryUserDOMHeight, height_max);
            usersQueryUI = (
                <div className='users-query-list' style={{height}}>
                    <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                                style={{height: '100%'}}
                    >
                        {this.state.queryUsers.map((user, index) => {
                            return (
                                <div
                                    key={index}
                                    className={'users-query-list-item' + (index === this.state.activeQueryIndex ? ' active' : '')}
                                    onClick={this.selectUser.bind(this, index)}
                                >
                                    {`${user.name} <${user.email}>`}
                                </div>
                            )
                        })}
                    </Scrollbars>
                </div>
            );
        }
        let selectedUsersUI = '';
        if (this.state.selectedUsers.length > 0) {
            selectedUsersUI = (
                <div>
                    <label>Selected people:</label>
                    <ul>
                        {this.state.selectedUsers.map((user, index) => {
                            return (
                                <li key={index}>{user.name}<span style={{fontSize: '10px', marginLeft: '5px', cursor: 'pointer'}} className='glyphicon glyphicon-remove' onClick={this.removeSelectedUser.bind(this, index)} /></li>
                            );
                        })}
                    </ul>
                </div>
            );
        }
        return (
            <ReactModal
                isOpen={this.props.showModal}
                contentLabel='Create group chat'
                onRequestClose={this.handleClose.bind(this)}
                style={{
                    overlay: {
                        top: '80px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }
                }}
                className='group-chat-modal'
            >
                <div className='group-chat-modal-header'>
                    <h3 style={{margin: 0}}>Create chat group</h3>
                    <span
                        className='glyphicon glyphicon-remove modal-close'
                        onClick={this.handleClose.bind(this)}
                    >
                    </span>
                </div>
                <form id='create-group-form' onSubmit={this.props.onCreate} autoComplete='off'>
                    <div className='group-chat-modal-body'>
                        <label htmlFor='user-search'>Add person:</label>
                        <div className='user-query-container'>
                            <input
                                type='text'
                                id='user-search'
                                className='modal-control'
                                onKeyDown={this.handleKeyPress.bind(this)}
                                onChange={this.searchUsers.bind(this)}
                                ref={input => this.userSearchInput = input}
                                value={this.state.userSearchQuery}
                                placeholder='Search person by name or email'
                            />
                            {usersQueryUI}
                        </div>
                        {selectedUsersUI}
                        <label htmlFor='group-name'>Group name:</label>
                        <input
                            type='text'
                            id='group-name'
                            className='modal-control'
                            onKeyDown={this.checkGroupName.bind(this)}
                            onChange={this.checkGroupName.bind(this)}
                            ref={input => this.groupNameInput = input}
                            value={this.state.groupName}
                        />
                        <label htmlFor='group-message'>Message:</label>
                        <textarea
                            id='group-message'
                            className='modal-control'
                            onKeyDown={this.checkGroupMessage.bind(this)}
                            onChange={this.checkGroupMessage.bind(this)}
                            ref={input => this.groupMessageInput = input}
                            value={this.state.groupMessage}
                        />
                    </div>
                    <div className='group-chat-modal-footer'>
                        <button className='chat-button create-group-button' type='submit' disabled={false}>
                            Create
                        </button>
                    </div>
                </form>
            </ReactModal>
        );
    }
}

export default GroupChatModal;
