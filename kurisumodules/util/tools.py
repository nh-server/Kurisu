from contextlib import contextmanager
from sqlite3 import Connection  # for type hinting


@contextmanager
def connwrap(conn: Connection, *, do_commit=True):
    cur = conn.cursor()
    yield cur
    cur.close()
    if do_commit:
        conn.commit()
