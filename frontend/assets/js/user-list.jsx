import React from 'react';


class UserList extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return '';
    }
}

function mapStateToProps (state) {
    return {
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
)(UserList);
