#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect('/cogs/kurisu.sqlite')

with open('schema.sql', 'r', encoding='utf-8') as f:
    schema = f.read()

conn.executescript(schema)
conn.commit()
conn.close()

print('Done!')