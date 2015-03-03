from pygibson import Client, NotFoundError, LockedError
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase, CreateError


SESSION_GIBSON_HOST = getattr(settings, 'SESSION_GIBSON_HOST', '127.0.0.1')
SESSION_GIBSON_PORT = getattr(settings, 'SESSION_GIBSON_PORT', 10128)
SESSION_GIBSON_TIMEOUT = getattr(settings, 'SESSION_GIBSON_TIMEOUT', 1000)
SESSION_GIBSON_PREFIX = getattr(settings, 'SESSION_GIBSON_PREFIX', 'session')
SESSION_GIBSON_UNIX_SOCKET = getattr(settings, 'SESSION_GIBSON_UNIX_SOCKET', None)


if SESSION_GIBSON_UNIX_SOCKET:
    session_backend = Client(unix_socket=SESSION_GIBSON_UNIX_SOCKET, timeout=SESSION_GIBSON_TIMEOUT)
else:
    session_backend = Client(host=SESSION_GIBSON_HOST, port=SESSION_GIBSON_PORT, timeout=SESSION_GIBSON_TIMEOUT)


class SessionStore(SessionBase):
    """
    Session storage backend based on the Gibson (http://gibson-db.in/)
    """

    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key=session_key)
        self.session_backend = session_backend

    @staticmethod
    def prefixed_key_name(session_key=None):
        if session_key:
            if SESSION_GIBSON_PREFIX:
                return '_'.join([SESSION_GIBSON_PREFIX, session_key])
            return session_key
        return None

    def exists(self, session_key):
        try:
            self.session_backend.get(self.prefixed_key_name(session_key))
            return True
        except NotFoundError:
            return False

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if must_create and self.exists(self._get_or_create_session_key()):
            raise CreateError
        key_2_save = self.prefixed_key_name(self._get_or_create_session_key())
        try:
            self.session_backend.set(
                key_2_save,
                self.encode(self._get_session(no_load=must_create)),
                self.get_expiry_age()
            )
        except LockedError:
            self.session_backend.unlock(key_2_save)
            self.session_backend.set(
                key_2_save,
                self.encode(self._get_session(no_load=must_create)),
                self.get_expiry_age()
            )

    def delete(self, session_key=None):
        key_2_delete = self.prefixed_key_name(session_key or self.session_key)
        if key_2_delete:
            try:
                self.session_backend.dl(key_2_delete)
            except LockedError:
                self.session_backend.unlock(key_2_delete)
                self.session_backend.dl(key_2_delete)
            except NotFoundError:
                pass
        return

    def load(self):
        try:
            return self.decode(self.session_backend.get(self.prefixed_key_name(self._get_or_create_session_key())))
        except NotFoundError:
            self.create()
            return {}

    @classmethod
    def clear_expired(cls):
        raise NotImplementedError
