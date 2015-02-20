# django-gibson-sessions
[Gibson](http://gibson-db.in/) session backend for [Django](https://www.djangoproject.com/)

### 1. Set proper engine
    
    SESSION_ENGINE = 'gibson_sessions.sessions'

### 2. Set common settings

    SESSION_GIBSON_TIMEOUT = 100
    SESSION_GIBSON_PREFIX = 'session'

### 3. Set connection settings

    SESSION_GIBSON_UNIX_SOCKET = '/var/run/gibson.sock'

OR

    SESSION_GIBSON_HOST = '127.0.0.1'
    SESSION_GIBSON_PORT = 10128

### 4. Enjoy
