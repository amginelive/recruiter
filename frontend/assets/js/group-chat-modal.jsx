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
            queryUserDOMHeight: 20,
            valid: {
                users: true,
                name: true,
                message: true
            }
        };
    }

    selectUser(index) {
        this.setState({
            valid: {...this.state.valid, users: true},
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
        if (event.key === 'Enter' || event.key === 'Tab') {
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
        if (groupMessage.length > 0) {
            this.setState({
                groupMessage,
                valid: {...this.state.valid, message: true}
            });
        }
    }

    checkGroupName() {
        const groupName = this.groupNameInput.value;
        if (groupName.length > 0) {
            this.setState({
                groupName,
                valid: {...this.state.valid, name: true}
            });
        }
    }

    resetState() {
        this.setState({
            groupName: '',
            groupMessage: '',
            userSearchQuery: '',
            selectedUsers: [],
            queryUsers: [],
            activeQueryIndex: 0,
            valid: {
                users: true,
                name: true,
                message: true
            }
        });
    }

    handleClose() {
        this.props.onClose();
        this.resetState();
    }

    handleCreate(event) {
        event.preventDefault();
        let valid = {...this.state.valid};
        if (this.state.groupName.length === 0) {
            valid.name = false;
        }
        if (this.state.groupMessage.length === 0) {
            valid.message = false;
        }
        if (this.state.selectedUsers.length === 0) {
            valid.users = false;
        }
        if (valid !== this.state.valid) {
            this.setState({valid});
        }
        setTimeout(() => {
            if (Object.values(this.state.valid).every(value => value)) {
                this.props.onCreate(this.state.selectedUsers.map(user => user.id), this.state.groupName, this.state.groupMessage);
                this.resetState();
            }
        });
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
                            );
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
                <form id='create-group-form' onSubmit={this.handleCreate.bind(this)} autoComplete='off'>
                    <div className='group-chat-modal-body'>
                        <label>Add person:</label>
                        <div id='user-search' className={'user-query-container modal-control' + (this.state.valid.users ? '' : ' error')}>
                            <input
                                type='text'
                                onKeyDown={this.handleKeyPress.bind(this)}
                                onChange={this.searchUsers.bind(this)}
                                ref={input => this.userSearchInput = input}
                                value={this.state.userSearchQuery}
                                placeholder='Search person by name or email'
                            />
                            {usersQueryUI}
                        </div>
                        {selectedUsersUI}
                        <label>Group name:</label>
                        <div id='group-name' className={'modal-control' + (this.state.valid.name ? '' : ' error')}>
                            <input
                                type='text'
                                onKeyDown={this.checkGroupName.bind(this)}
                                onChange={this.checkGroupName.bind(this)}
                                ref={input => this.groupNameInput = input}
                                value={this.state.groupName}
                            />
                        </div>
                        <label>Message:</label>
                        <div id='group-message' className={'modal-control' + (this.state.valid.message ? '' : ' error')}>
                            <textarea
                                onKeyDown={this.checkGroupMessage.bind(this)}
                                onChange={this.checkGroupMessage.bind(this)}
                                ref={input => this.groupMessageInput = input}
                                value={this.state.groupMessage}
                            />
                        </div>
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
