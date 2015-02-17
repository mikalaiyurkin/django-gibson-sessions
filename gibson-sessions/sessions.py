from pygibson import Client, NotFoundError, LockedError
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase


SESSION_GIBSON_HOST = getattr(settings, 'SESSION_GIBSON_HOST', '127.0.0.1')
SESSION_GIBSON_PORT = getattr(settings, 'SESSION_GIBSON_PORT', 10128)
SESSION_GIBSON_TIMEOUT = getattr(settings, 'SESSION_GIBSON_TIMEOUT', 1000)
SESSION_GIBSON_PREFIX = getattr(settings, 'SESSION_GIBSON_PREFIX', 'session')
SESSION_GIBSON_UNIX_SOCKET = getattr(settings, 'SESSION_GIBSON_UNIX_SOCKET', None)


if SESSION_GIBSON_UNIX_SOCKET:
    # Connection via socket file is preferred.
    session_backend = Client(unix_socket=SESSION_GIBSON_UNIX_SOCKET, timeout=SESSION_GIBSON_TIMEOUT)
else:
    session_backend = Client(host=SESSION_GIBSON_HOST, port=SESSION_GIBSON_PORT, timeout=SESSION_GIBSON_TIMEOUT)


class SessionStore(SessionBase):
    """
    Session storage backend based on the Gibson (http://gibson-db.in/)
    """

    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key=session_key)

    @staticmethod
    def prefixed_key_name(session_key=None):
        """
        Return properly built session key name
        """
        if session_key:
            if SESSION_GIBSON_PREFIX:
                return '.'.join([SESSION_GIBSON_PREFIX, session_key])
            return session_key
        return None

    def exists(self, session_key):
        """
        Returns True if the given session_key already exists.
        """
        try:
            session_backend.get(self.prefixed_key_name(session_key))
            return True
        except NotFoundError:
            return False

    def create(self):
        """
        Creates a new session instance. Guaranteed to create a new object with
        a unique key and will have saved the result once (with empty data)
        before the method returns.
        """
        raise NotImplementedError

    def save(self, must_create=False):
        """
        Saves the session data. If 'must_create' is True, a new session object
        is created (otherwise a CreateError exception is raised). Otherwise,
        save() can update an existing object with the same key.
        """
        raise NotImplementedError

    def delete(self, session_key=None):
        """
        Deletes the session data under this key. If the key is None, the
        current session key value is used.
        """
        key_2_delete = self.prefixed_key_name(session_key or self.session_key)
        if key_2_delete:
            try:
                session_backend.dl(key_2_delete)
            except LockedError:
                # session should not be locked
                session_backend.unlock(key_2_delete)
                session_backend.dl(key_2_delete)
            except NotFoundError:
                pass
        return

    def load(self):
        """
        Loads the session data and returns a dictionary.
        """
        raise NotImplementedError

    @classmethod
    def clear_expired(cls):
        """
        Remove expired sessions from the session store.

        If this operation isn't possible on a given backend, it should raise
        NotImplementedError. If it isn't necessary, because the backend has
        a built-in expiration mechanism, it should be a no-op.
        """
        raise NotImplementedError
