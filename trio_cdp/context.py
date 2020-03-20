import contextvars


connection_context: contextvars.ContextVar = contextvars.ContextVar('connection_context')
session_context: contextvars.ContextVar = contextvars.ContextVar('session_context')


def get_connection_context(fn_name):
    '''
    Look up the current connection. If there is no current connection, raise a
    ``RuntimeError`` with a helpful message.
    '''
    try:
        return connection_context.get()
    except LookupError:
        raise RuntimeError(f'{fn_name}() must be called in a connection context.')


def get_session_context(fn_name):
    '''
    Look up the current session. If there is no current session, raise a
    ``RuntimeError`` with a helpful message.
    '''
    try:
        return session_context.get()
    except LookupError:
        raise RuntimeError(f'{fn_name}() must be called in a session context.')


def set_global_connection(connection):
    '''
    Install ``connection`` in the root context so that it will become the default
    connection for all tasks. This is generally not recommended, except it may be
    necessary in certain use cases such as running inside Jupyter notebook.
    '''
    global connection_context
    connection_context = contextvars.ContextVar('connection_context',
        default=connection)


def set_global_session(session):
    '''
    Install ``session`` in the root context so that it will become the default
    session for all tasks. This is generally not recommended, except it may be
    necessary in certain use cases such as running inside Jupyter notebook.
    '''
    global session_context
    session_context = contextvars.ContextVar('session_context', default=session)
