import json
from configparser import ConfigParser
import sqlite3
from sys import exit
import discord
from discord.ext import commands
import os

config = ConfigParser()
config.read("config.ini")

roles = {
    'Probation': None,
    'Muted': None,
    'No-Help': None,
    'no-elsewhere': None,
    'No-Memes': None,
    'No-Embed': None,
    'Small Help': None,}

DATABASE_NAME = 'data/kurisu.sqlite'
bot = commands.Bot(('.', '!'), description="Database Converter!")

@bot.event
async def on_ready():
    if not os.path.isfile(DATABASE_NAME):
        # read schema, open db, init
        print(f'Creating database {DATABASE_NAME}')
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        dbcon = sqlite3.connect(DATABASE_NAME)
        dbcon.executescript(schema)
        dbcon.commit()
        c = dbcon.cursor()
        print(f'{DATABASE_NAME} initialized')
    else:
        # just open db, no setup
        dbcon = sqlite3.connect(DATABASE_NAME)
        c = dbcon.cursor()

    for n in roles.keys():
        roles[n] = discord.utils.get(bot.guild.roles, name=n)

    with open("data/restrictions.json", "r") as f:
        rsts = json.load(f)
    with open("data/warnsv2.json", "r") as f:
        warns = json.load(f)
    with open("data/helpers.json", "r") as f:
        helpers = json.load(f)
    with open("data/softbans.json", "r") as f:
        softbans = json.load(f)
    with open("data/staff.json", "r") as f:
        staff = json.load(f)
    with open("data/timenohelp.json", "r") as f:
        tnohelp = json.load(f)
    with open("data/timebans.json", "r") as f:
        timebans = json.load(f)
    with open("data/timemutes.json", "r") as f:
        timemutes = json.load(f)
    with open("data/watch.json", "r") as f:
        watch = json.load(f)

    # same queries as the database class but no commit until the very end
    for id in rsts.keys():
        for rolename in rsts[id]:
            role = roles[rolename]
            if c.execute ('SELECT user_id FROM permanent_roles WHERE user_id=? AND role_id=?',
                                  (id, role.id)).fetchone() is None:
                c.execute ('INSERT INTO permanent_roles VALUES(?, ?)', (id, role.id))

    for id in warns.keys():
        for warn in warns[id]["warns"]:
            c.execute ('INSERT INTO warns VALUES(?, ?, ?, ?)', (id, warn['issuer_id'], warn['reason'], warn['timestamp']))

    for id in helpers.keys():
        try:
            c.execute ('INSERT INTO helpers VALUES(?, ?)', (id, helpers[id]))
        except sqlite3.IntegrityError:
            c.execute ('UPDATE helpers SET console=? WHERE user_id=?', (helpers[id], id,))
    for id in softbans.keys():
        try:
            c.execute ('INSERT INTO softbans VALUES(?, ? , ?, ?)', (id, softbans[id]['issuer_id'], softbans[id]['reason'], softbans[id]["timestamp"]))
        except sqlite3.IntegrityError:
            continue

    for id in staff:
        try:
            c.execute ('INSERT INTO staff VALUES(?, ?)', (id, staff[id]))
        except sqlite3.IntegrityError:
            c.execute ('UPDATE staff SET position=? WHERE user_id=?', (staff[id], id))

    for id in tnohelp:
        # assume old warns are older than the ones in the database
        if c.execute ('SELECT 1 FROM timed_restrictions WHERE user_id=? AND type=?',
                              (id, 'timenohelp')).fetchone() is None:
            c.execute ('INSERT INTO timed_restrictions VALUES(?, ?, ?, ?)', (id, tnohelp[id], 'timenohelp', 0))

    for id in timebans:
        # assume old warns are older than the ones in the database
        if c.execute ('SELECT 1 FROM timed_restrictions WHERE user_id=? AND type=?',
                              (id, 'timeban')).fetchone() is None:
            c.execute ('INSERT INTO timed_restrictions VALUES(?, ?, ?, ?)',
                               (id, timebans[id], 'timeban', 0))

    for id in timemutes:
        # assume old warns are older than the ones in the database
        if c.execute ('SELECT 1 FROM timed_restrictions WHERE user_id=? AND type=?',
                              (id, 'timemute')).fetchone() is None:
            c.execute ('INSERT INTO timed_restrictions VALUES(?, ?, ?, ?)',
                               (id, timemutes[id], 'timemute', 0))

    for id in watch.keys():
        try:
            c.execute ('INSERT INTO watchlist VALUES(?)', (id,))
        except sqlite3.IntegrityError:
            continue
    print('Data converted successfully!')
    dbcon.commit()
    await bot.close()


def main():

    print(f'Starting Database Converter')
    bot.run(config['Main']['token'])

if __name__=='__main__':
    exit(main())
