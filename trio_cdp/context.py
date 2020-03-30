from contextlib import contextmanager
import contextvars


_connection_context: contextvars.ContextVar = contextvars.ContextVar('connection_context')
_session_context: contextvars.ContextVar = contextvars.ContextVar('session_context')




def get_connection_context(fn_name):
    '''
    Look up the current connection. If there is no current connection, raise a
    ``RuntimeError`` with a helpful message.
    '''
    try:
        return _connection_context.get()
    except LookupError:
        raise RuntimeError(f'{fn_name}() must be called in a connection context.')


def get_session_context(fn_name):
    '''
    Look up the current session. If there is no current session, raise a
    ``RuntimeError`` with a helpful message.
    '''
    try:
        return _session_context.get()
    except LookupError:
        raise RuntimeError(f'{fn_name}() must be called in a session context.')


@contextmanager
def connection_context(connection):
    ''' This context manager installs ``connection`` as the session context for the current
    Trio task. '''
    token = _connection_context.set(connection)
    try:
        yield
    finally:
        _connection_context.reset(token)


@contextmanager
def session_context(session):
    ''' This context manager installs ``session`` as the session context for the current
    Trio task. '''
    token = _session_context.set(session)
    try:
        yield
    finally:
        _session_context.reset(token)


def set_global_connection(connection):
    '''
    Install ``connection`` in the root context so that it will become the default
    connection for all tasks. This is generally not recommended, except it may be
    necessary in certain use cases such as running inside Jupyter notebook.
    '''
    global _connection_context
    _connection_context = contextvars.ContextVar('_connection_context',
        default=connection)


def set_global_session(session):
    '''
    Install ``session`` in the root context so that it will become the default
    session for all tasks. This is generally not recommended, except it may be
    necessary in certain use cases such as running inside Jupyter notebook.
    '''
    global _session_context
    _session_context = contextvars.ContextVar('_session_context', default=session)
