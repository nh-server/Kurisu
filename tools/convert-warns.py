#!/usr/bin/env python3
import json
import sqlite3
from argparse import ArgumentParser
from datetime import datetime

from discord.utils import time_snowflake

parser = ArgumentParser(description='Convert warnsv2.json into SQLite entries for Kurisu2. '
                                    'Adds both Warns and Action Log entries. '
                                    'The database should have already been created by Kurisu2.')
parser.add_argument('json', help='warnsv2 JSON file')
parser.add_argument('--db', help='Kurisu2 SQLite database (Default: kurisu2_data.sqlite)', default='kurisu2_data.sqlite')

args = parser.parse_args()

print(f'Loading {args.json}...')
with open(args.json, 'r') as f:
    warns_org = json.load(f)

warns = []
actions = []
print('Converting warns to entries...')
for i, uw in warns_org.items():
    for w in uw['warns']:
        date = datetime.strptime(w['timestamp'], '%Y-%m-%d %H:%M:%S')
        issuer = int(w['issuer_id'])
        target = int(i)
        warn_entry = {'warn_id': time_snowflake(date), 'user_id': target, 'issuer': issuer, 'reason': w['reason']}
        action_entry = {'entry_id': time_snowflake(date), 'user_id': issuer, 'target_id': target, 'kind': 'warn',
                        'description': w['reason'], 'extra': None}
        warns.append(warn_entry)
        actions.append(action_entry)

print('Sorting warns...')
warns.sort(key=lambda x: x['warn_id'])
actions.sort(key=lambda x: x['entry_id'])

c = sqlite3.connect(args.db)
cc = c.cursor()

print('Inserting into warns table...')
for e in warns:
    cc.execute('INSERT INTO warns VALUES (:warn_id, :user_id, :issuer, :reason)', e)

print('Inserting into actions_log table...')
for e in actions:
    cc.execute('INSERT INTO actions_log VALUES (:entry_id, :user_id, :target_id, :kind, :description, :extra)', e)

print('Committing to database...')
c.commit()

print('Done.')
