from contextlib import contextmanager
from sqlite3 import Connection  # for type hinting


@contextmanager
def connwrap(conn: Connection, *, do_commit=True):
    """Wrap an sqlite3.Connection object to yield a Cursor, then close at the end of the context."""
    # this is probably not necessary
    cur = conn.cursor()
    yield cur
    cur.close()
    if do_commit:
        conn.commit()
