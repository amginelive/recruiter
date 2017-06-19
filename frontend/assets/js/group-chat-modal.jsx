import React from 'react';
import ReactModal from 'react-modal';


const GroupChatModal = (props) => {
    return (
        <ReactModal
            isOpen={props.showModal}
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
                <span className='glyphicon glyphicon-remove modal-close' onClick={props.onClose}></span>
            </div>
        </ReactModal>
    );
};

export default GroupChatModal;
