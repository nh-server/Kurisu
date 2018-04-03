from contextlib import contextmanager
from sqlite3 import Connection  # for type hinting


@contextmanager
def connwrap(conn: Connection):
    """Wrap an sqlite3.Connection object to yield a Cursor, then close at the end of the context."""
    # this is probably not necessary
    with conn:
        cur = conn.cursor()
        yield cur
        cur.close()


# https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
# but modified to be an f-string
def ordinal(n: int) -> str:
    # noinspection SpellCheckingInspection
    return f'{n}{"tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]}'


# http://stackoverflow.com/questions/3411771/multiple-character-replace-with-python
chars = r'\`*_<>#@:~'


def escape_name(name) -> str:
    name = str(name)
    for c in chars:
        if c in name:
            name = name.replace(c, '\\' + c)
    return name.replace('@', '@\u200b')  # prevent mentions
