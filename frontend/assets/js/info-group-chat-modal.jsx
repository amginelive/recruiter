import React from 'react';
import ReactModal from 'react-modal';


class InfoGroupChatModal extends React.Component {
    constructor(props) {
        super(props);
    }

    handleClose() {
        this.props.onClose();
    }

    handleKick(user_id) {
        this.props.onKick(parseInt(user_id));
    }

    handleInvite(user_id) {
        this.props.onInvite(parseInt(user_id));
    }

    renderUsersGroup(users, header, owner, reinvite = false) {
        if (users.size === 0) {
            return <div />;
        }
        const admin = this.props.users.get('self') === owner;
        users = users.sortBy((value, key) => key, (a, b) => {return parseInt(a) === owner ? -1 : (parseInt(b) === owner ? 1 : 0)});
        const merged_users = this.props.users.merge(this.props.users.get('extra')).delete('extra').delete('self');
        return (
            <ul>
                <label>{header}</label>
                {users.map((user, user_id) => {
                    return (
                        <li key={user_id}>
                            {merged_users.get(user_id.toString()).get('name') + (parseInt(user_id) === owner ? ' (owner)' : '')}
                            {!reinvite && admin && parseInt(user_id) !== owner ? <span style={{fontSize: '10px', marginLeft: '5px', cursor: 'pointer'}} className='glyphicon glyphicon-remove' onClick={this.handleKick.bind(this, user_id)} /> : ''}
                            {reinvite && admin ? <span style={{fontSize: '10px', marginLeft: '5px', cursor: 'pointer'}} className='glyphicon glyphicon-repeat' onClick={this.handleInvite.bind(this, user_id)} /> : ''}
                        </li>
                    );
                }).toArray()}
            </ul>
        );
    }

    render() {
        const {chats} = this.props;
        const chat = chats.get('groups').get(chats.get('activeChat').toString());
        if (!chat) {
            return <div />;
        }
        const active_users = chat.get('users').filter(user => user.get('status') === 0);
        const pending_users = chat.get('users').filter(user => user.get('status') === 1);
        const declined_users = chat.get('users').filter(user => user.get('status') === 2);
        return (
            <ReactModal
                isOpen={this.props.showModal}
                contentLabel='Group chat info'
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
                    <h3 style={{margin: 0}}>Chat group info</h3>
                    <span
                        className='glyphicon glyphicon-remove modal-close'
                        onClick={this.handleClose.bind(this)}
                    >
                    </span>
                </div>
                <div className='group-chat-modal-footer'>
                    {this.renderUsersGroup(active_users, 'Joined users:', chat.get('owner'))}
                </div>
                <div className='group-chat-modal-footer'>
                    {this.renderUsersGroup(pending_users, 'Pending invites:', chat.get('owner'))}
                </div>
                <div className='group-chat-modal-footer'>
                    {this.renderUsersGroup(declined_users, 'Declined users:', chat.get('owner'), true)}
                </div>
            </ReactModal>
        );
    }
}

export default InfoGroupChatModal;
