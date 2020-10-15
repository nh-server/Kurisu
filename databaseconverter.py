import sqlite3
import asyncio
import discord
import sys
import datetime
import os
from utils import models
from utils.models import db
from configparser import ConfigParser

SQLITE_FILE = './data/kurisu.sqlite'

IS_DOCKER = os.environ.get('IS_DOCKER', 0)

if IS_DOCKER:
    db_user_file = os.environ.get('DB_USER')
    db_password_file = os.environ.get('DB_PASSWORD')
    if db_user_file and db_password_file:
        with open(db_user_file, 'r', encoding='utf-8') as f:
            db_user = f.readline().strip()
        with open(db_password_file, 'r', encoding='utf-8') as f:
            db_password = f.readline().strip()
        DATABASE_URL = f"postgresql://{db_user}:{db_password}@db/{db_user}"
    else:
        sys.exit('Database user and database password files paths need to be proved')
else:
    config = ConfigParser()
    config.read("data/config.ini")
    DATABASE_URL = config['Main']['database_url']


def has_seconds(str_timestamp):
    return "." in str_timestamp.split(":")[2]


async def main():
    await db.set_bind(DATABASE_URL)
    await db.gino.drop_all()
    await db.gino.create_all()
    conn = sqlite3.connect(SQLITE_FILE)
    c = conn.cursor()

    users = []

    # Friend Codes
    c.execute('SELECT * FROM friend_codes')
    data = c.fetchall()
    fc_entries = []
    if data:
        for entry in data:
            fc_entries.append(dict(id=entry[0], fc_3ds=entry[1]))
            users.append(entry[0])

    # permanent roles
    c.execute('SELECT * FROM permanent_roles')
    data = c.fetchall()
    perm_entries = []
    roles = []
    if data:
        for entry in data:
            if entry[1] not in roles:
                roles.append(entry[1])
            if entry[0] not in users:
                users.append(entry[0])
            # There is duplicate entries for some reason
            if entry not in perm_entries:
                perm_entries.append(entry)
        await models.Role.insert().gino.all([dict(id=id) for id in roles])

    # softban
    c.execute('SELECT * FROM softbans')
    data = c.fetchall()
    softban_entries = []
    if data:
        for entry in data:
            softban_entries.append(
                dict(id=discord.utils.time_snowflake(
                    datetime.datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S.%f' if has_seconds(
                        entry[3]) else '%Y-%m-%d %H:%M:%S')),
                    user=entry[0], issuer=entry[1],
                    reason=entry[2]))
            if entry[0] not in users:
                users.append(entry[0])
            if entry[1] not in users:
                users.append(entry[1])

    # Timed Restricions
    c.execute('SELECT * FROM timed_restrictions')
    data = c.fetchall()
    timeres_entries = []
    if data:
        for i, entry in enumerate(data):
            timeres_entries.append(
                dict(id=discord.utils.time_snowflake(datetime.datetime.now() + datetime.timedelta(0, i)), user=entry[0],
                     type=entry[2], end_date=datetime.datetime.strptime(entry[1], '%Y-%m-%d %H:%M:%S.%f' if has_seconds(
                        entry[1]) else '%Y-%m-%d %H:%M:%S'), alerted=bool(entry[3])))
            if entry[0] not in users:
                users.append(entry[0])

    # Warns
    c.execute('SELECT * FROM warns')
    data = c.fetchall()
    warn_entries = []
    if data:
        for entry in data:
            warn_entries.append(
                dict(id=entry[0], user=entry[1], issuer=entry[2], reason=entry[3]))
            if entry[1] not in users:
                users.append(entry[1])
            if entry[2] not in users:
                users.append(entry[2])

    # Staff
    c.execute('SELECT * FROM staff')
    data = c.fetchall()
    staff_entries = []
    staff = []
    if data:
        for entry in data:
            staff_entries.append(dict(id=entry[0], position=entry[1]))
            staff.append(entry[0])
            if entry[0] not in users:
                users.append(entry[0])

    # Helpers
    c.execute('SELECT * FROM helpers')
    data = c.fetchall()
    helper_entries = []
    if data:
        for entry in data:
            try:
                index = staff.index(entry[0])
            except:
                index = -1
            if index >= 0:
                staff_entries[index]['console'] = entry[1]
            else:
                helper_entries.append(dict(id=entry[0], position='Helper', console=entry[1]))
                if entry[0] not in users:
                    users.append(entry[0])

    # channels
    c.execute('SELECT * FROM nofilter')
    data = c.fetchall()
    if data:
        channel_entries = [dict(id=entry[0], nofilter=True) for entry in data]
        await models.Channel.insert().gino.all(channel_entries)

    # wordfilter
    c.execute('SELECT * FROM wordfilter')
    data = c.fetchall()
    if data:
        word_entries = [dict(word=entry[0], kind=entry[1]) for entry in data]
        await models.FilteredWord.insert().gino.all(word_entries)

    # invitefilter
    c.execute('SELECT * FROM invitefilter')
    data = c.fetchall()
    if data:
        invite_entries = [dict(code=entry[0], uses=entry[3], alias=entry[2]) for entry in data]
        await models.ApprovedInvite.insert().gino.all(invite_entries)

    # flags
    c.execute('SELECT * FROM flags')
    data = c.fetchall()
    if data:
        flag_entries = [dict(name=entry[0], value=bool(entry[1])) for entry in data]
        await models.Flag.insert().gino.all(flag_entries)

    await models.Member.insert().gino.all([dict(id=id) for id in users])
    await models.FriendCode.insert().gino.all(fc_entries)
    await models.Staff.insert().gino.all(staff_entries)
    await models.TimedRestriction.insert().gino.all(timeres_entries)
    await models.Warn.insert().gino.all(warn_entries)
    await models.PermanentRole.insert().gino.all([dict(user_id=user, role_id=role) for user, role in perm_entries])
    await models.Softban.insert().gino.all(softban_entries)
    await models.Staff.insert().gino.all(helper_entries)

    # Watchlist
    c.execute('SELECT * FROM watchlist')
    data = c.fetchall()
    mb_entries = []
    if data:

        async with db.transaction() as tx:
            for entry in data:
                if entry[0] in users:
                    await db.status(f"UPDATE members SET watched='true' where id={entry[0]}")
                else:
                    mb_entries.append(dict(id=entry[0], watched=True))
        await models.Member.insert().gino.all(mb_entries)


asyncio.get_event_loop().run_until_complete(main())
