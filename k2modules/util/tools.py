

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
