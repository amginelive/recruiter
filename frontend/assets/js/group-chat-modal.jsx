import React from 'react';
import ReactModal from 'react-modal';
import { Scrollbars } from 'react-custom-scrollbars';


class GroupChatModal extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            userSearchQuery: '',
            selectedUsers: [],
            queryUsers: [],
            activeQueryIndex: 0
        };
    }

    handleKeyPress(event) {
        if (event.key === 'ArrowDown') {
            if (this.state.queryUsers.length > 1) {
                if (this.state.activeQueryIndex < this.state.queryUsers.length - 1) {
                    this.setState({activeQueryIndex: this.state.activeQueryIndex + 1});
                } else {
                    this.setState({activeQueryIndex: 0});
                }
            }
            event.preventDefault();
            return;
        }
        if (event.key === 'ArrowUp') {
            if (this.state.queryUsers.length > 1) {
                if (this.state.activeQueryIndex > 0) {
                    this.setState({activeQueryIndex: this.state.activeQueryIndex - 1});
                } else {
                    this.setState({activeQueryIndex: this.state.queryUsers.length - 1});
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
            if (this.state.queryUsers.length > 0) {
                this.setState({
                    selectedUsers: [...this.state.selectedUsers, this.state.queryUsers[this.state.activeQueryIndex]],
                    activeQueryIndex: 0,
                    userSearchQuery: '',
                    queryUsers: []
                });
                return;
            }
            event.preventDefault();
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
                let queryUsers = users.filter(user => user.get('name').toLowerCase().includes(userSearchQuery.toLowerCase()));
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

    render() {
        let usersQueryUI = '';
        if (this.state.queryUsers.length > 0) {
            usersQueryUI = (
                <div className='users-query-list'>
                    <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                                style={{height: '100%'}}
                                autoHide autoHideTimeout={1000}
                                autoHideDuration={200}>
                        {this.state.queryUsers.map((user, index) => {
                            return (
                                <div key={index} className={'users-query-list-item' + (index === this.state.activeQueryIndex ? ' active' : '')}>{user.name}</div>
                            )
                        })}
                    </Scrollbars>
                </div>
            );
        }
        return (
            <ReactModal
                isOpen={this.props.showModal}
                contentLabel='Create group chat'
                shouldCloseOnOverlayClick={false}
                style={{
                    overlay: {
                        top: '100px'
                    }
                }}
                className='group-chat-modal'
            >
                <div className='group-chat-modal-header'>
                    <span className='glyphicon glyphicon-remove modal-close' onClick={this.props.onClose}></span>
                </div>
                <div className='group-chat-modal-body'>
                    <ul>
                        {this.state.selectedUsers.map((user, index) => {
                            return (
                                <li key={index}>{user.name}<span onClick={this.removeSelectedUser.bind(this, index)}>x</span></li>
                            );
                        })}
                    </ul>
                    <label htmlFor='user-search'>Add user:</label>
                    <input
                        type='text'
                        id='user-search'
                        onKeyDown={this.handleKeyPress.bind(this)}
                        onChange={this.searchUsers.bind(this)}
                        ref={input => this.userSearchInput = input}
                        value={this.state.userSearchQuery}
                    />
                    {usersQueryUI}
                </div>
            </ReactModal>
        );
    }
}

export default GroupChatModal;
