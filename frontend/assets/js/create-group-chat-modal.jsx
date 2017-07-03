import React from 'react';
import ReactModal from 'react-modal';

import UserQueryForm from './user-query-form.jsx';


class CreateGroupChatModal extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            groupName: '',
            groupMessage: '',
            valid: {
                users: true,
                name: true,
                message: true
            },
            selectedUsers: []
        };
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

    userQueryChange(users) {
        const valid = users.length > 0;
        this.setState({
            selectedUsers: users,
            valid: {...this.state.valid, users: valid}
        });
    }

    render() {
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
                        <UserQueryForm
                            id='user-search'
                            users={this.props.users.delete('self').delete('extra').delete(this.props.users.get('self').toString())}
                            onChange={this.userQueryChange.bind(this)}
                            valid={this.state.valid.users}
                        />
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
                        <button className='chat-button modal-button' type='submit' disabled={false}>
                            Create
                        </button>
                    </div>
                </form>
            </ReactModal>
        );
    }
}

export default CreateGroupChatModal;
