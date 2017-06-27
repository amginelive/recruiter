import React from 'react';
import ReactModal from 'react-modal';


class LeaveGroupChatModal extends React.Component {
    constructor(props) {
        super(props);
    }

    handleClose() {
        this.props.onClose();
    }

    handleLeave() {
        this.props.onLeave(this.props.group_id);
    }

    render() {
        return (
            <ReactModal
                isOpen={this.props.showModal}
                contentLabel='Leave group chat'
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
                    <h3 style={{margin: 0}}>Leave chat group</h3>
                    <span
                        className='glyphicon glyphicon-remove modal-close'
                        onClick={this.handleClose.bind(this)}
                    >
                    </span>
                </div>
                <div className='group-chat-modal-footer'>
                    <button className='chat-button create-group-button' onClick={this.handleLeave.bind(this)}>
                        Yes
                    </button>
                    <button className='chat-button create-group-button' onClick={this.handleClose.bind(this)}>
                        No
                    </button>
                </div>
            </ReactModal>
        );
    }
}

export default LeaveGroupChatModal;
