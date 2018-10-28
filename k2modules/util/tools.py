from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlite3 import Connection
    from typing import Callable


@contextmanager
def connwrap(conn: 'Connection'):
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


# unsigned to signed 64-bit
def u2s(i: int):
    if i & 0x8000000000000000:
        # unlikely to happen, I think
        return int.from_bytes(i.to_bytes(8, 'little'), 'little', signed=True)
    return i


# signed to unsigned 64-bit
def s2u(i: int):
    return i & 0xFFFFFFFFFFFFFFFF
