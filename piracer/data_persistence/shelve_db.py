from sqlitedict import SqliteDict


def _get_db_location():
    db_location = '/home/main/slamcar-worker/data/settings_store.sqlite3'
    return db_location


def reset_db(*, location=None):
    if not location:
        location = _get_db_location()
    # empty database by truncating the file
    with open(location, 'w') as _:
        pass


def get(key, default=None, *, location=None):
    if not location:
        location = _get_db_location()
    with SqliteDict(location, autocommit=True) as store:
        val = store.get(key, default)
    return val


def set(key, value, *, location=None):
    if not location:
        location = _get_db_location()
    with SqliteDict(location, autocommit=True) as store:
        store[key] = value
