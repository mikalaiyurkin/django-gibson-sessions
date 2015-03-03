from pygibson import PyGibsonError
from nose.tools import eq_, ok_
from django.conf import settings
settings.configure()


def set_connection():

    try:
        settings.SESSION_GIBSON_TIMEOUT = 100

        try:
            # set IPC connection settings
            settings.SESSION_GIBSON_UNIX_SOCKET = '/var/run/gibson.sock'
            from gibson_sessions.sessions import SessionStore
            ss = SessionStore()
        except PyGibsonError:
            # set TCP connection settings
            settings.SESSION_GIBSON_HOST = '127.0.0.0'
            settings.SESSION_GIBSON_PORT = 10128
            from gibson_sessions.sessions import SessionStore
            ss = SessionStore()

        ss.session_backend.ping()
        return ss
    except PyGibsonError:
        return None


def modification_test():
    storage = set_connection()
    ok_(storage)
    eq_(storage.modified, False)
    storage['gibson'] = 'modified'
    eq_(storage.modified, True)
    eq_(storage['gibson'], 'modified')


def create_and_delete_test():
    storage = set_connection()
    ok_(storage)
    storage.save()
    eq_(storage.exists(storage.session_key), True)
    storage.delete()
    eq_(storage.exists(storage.session_key), False)


def create_and_delete_locked_test():
    storage = set_connection()
    ok_(storage)
    storage.save()
    eq_(storage.exists(storage.session_key), True)
    storage.session_backend.lock(storage.prefixed_key_name(storage.session_key), 60)
    storage.delete()
    eq_(storage.exists(storage.session_key), False)


def update_locked_test():
    storage = set_connection()
    ok_(storage)
    storage.save()
    eq_(storage.exists(storage.session_key), True)
    storage['gibson'] = 'before_lock'
    storage.session_backend.lock(storage.prefixed_key_name(storage.session_key), 60)
    storage['gibson'] = 'ignore_lock'
    storage.save()
    eq_(storage['gibson'], 'ignore_lock')


def expiration_test():
    import time
    storage = set_connection()
    ok_(storage)
    storage.set_expiry(1)
    storage.save()
    eq_(storage.exists(storage.session_key), True)
    time.sleep(2)
    eq_(storage.exists(storage.session_key), False)