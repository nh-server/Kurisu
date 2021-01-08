import datetime

from . import models
from discord import utils, TextChannel


def generate_id():
    return utils.time_snowflake(datetime.datetime.now())


async def add_permanent_role(user_id: int, role_id: int):
    await add_dbmember_if_not_exist(user_id)
    if not await models.PermanentRole.query.where((models.PermanentRole.user_id == user_id) & (
            models.PermanentRole.role_id == role_id)).gino.first():
        return await models.PermanentRole.create(user_id=user_id, role_id=role_id)


async def remove_permanent_role(user_id: int, role_id: int):
    permanent_role = await models.PermanentRole.query.where((models.PermanentRole.user_id == user_id) & (
            models.PermanentRole.role_id == role_id)).gino.first()
    if permanent_role:
        await permanent_role.delete()
        return permanent_role


async def get_permanent_roles(user_id: int):
    db_member = await get_dbmember(user_id)
    if db_member:
        return await models.Role.query.where((models.Role.id == models.PermanentRole.role_id) & (models.PermanentRole.user_id == db_member.id)).gino.all()


async def add_staff(user_id: int, position: str):
    await add_dbmember_if_not_exist(user_id)
    staff = await get_staff(user_id) or await get_helper(user_id)
    if staff:
        await staff.update(position=position).apply()
    else:
        await models.Staff.create(id=user_id, position=position)


async def add_helper(user_id: int, position: str, console: str = None):
    await add_dbmember_if_not_exist(user_id)
    if staff := await get_staff(user_id):
        await staff.update(console=console).apply()
    else:
        await models.Staff.create(id=user_id, position=position, console=console)


async def remove_staff(user_id: int):
    staff = await get_staff(user_id)
    if staff:
        if staff.console:
            await staff.update(position="Helper").apply()
        else:
            await staff.delete()


async def remove_helper(user_id: int):
    helper = await get_helper(user_id)
    if helper:
        if helper.position != "Helper":
            await helper.update(console=None).apply()
        else:
            await helper.delete()


async def get_staff_all():
    return await models.Staff.query.where(models.Staff.position != 'Helper').gino.all()


async def get_staff(user_id: int):
    return await models.Staff.query.where(
        (models.Staff.position != 'Helper') & (models.Staff.id == user_id)).gino.first()


async def get_helpers():
    return await models.Staff.query.where(models.Staff.console.isnot(None)).gino.all()


async def get_helper(user_id: int):
    return await models.Staff.query.where(models.Staff.id == user_id).gino.first()


async def add_warn(user_id: int, issuer_id: int, reason: str):
    await add_dbmember_if_not_exist(user_id)
    await add_dbmember_if_not_exist(issuer_id)
    await models.Warn.create(id=generate_id(), user=user_id, issuer=issuer_id, reason=reason)


async def copy_warn(user_id: int, warn: models.Warn):
    await add_dbmember_if_not_exist(user_id)
    warn.id = utils.time_snowflake(utils.snowflake_time(warn.id) + datetime.timedelta(milliseconds=1))
    while await get_warn(warn.id):
        warn.id = utils.time_snowflake(utils.snowflake_time(warn.id) + datetime.timedelta(milliseconds=1))
    warn.user = user_id
    await warn.create()


async def get_warn(warn_id: int):
    return await models.Warn.get(warn_id)


async def get_warns(user_id: int):
    return await models.Warn.query.where(models.Warn.user == user_id).gino.all()


async def remove_warn_id(user_id: int, index: int):
    warn = await models.Warn.query.where(models.Warn.user == user_id).offset(index - 1).gino.first()
    await warn.delete()


async def remove_warns(user_id: int):
    n_warns = await (models.db.select([models.db.func.count()]).where(models.Warn.user == user_id).gino.scalar())
    if n_warns:
        await models.Warn.delete.where(models.Warn.user == user_id).gino.status()
    return n_warns


async def add_timed_restriction(user_id: int, end_date: datetime.datetime, type: str):
    await add_dbmember_if_not_exist(user_id)
    await models.TimedRestriction.create(id=generate_id(), user=user_id, type=type,
                                         end_date=end_date)


async def get_time_restrictions_by_user(user_id: int):
    return await models.TimedRestriction.query.where(models.TimedRestriction.user == user_id).gino.all()


async def get_time_restrictions_by_user_type(user_id: int, type: str):
    return await models.TimedRestriction.query.where((models.TimedRestriction.user == user_id) & (
            models.TimedRestriction.type == type)).gino.first()


async def get_time_restrictions_by_type(type: str):
    return await models.TimedRestriction.query.where(models.TimedRestriction.type == type).gino.all()


async def remove_timed_restriction(user_id: int, type: str):
    time_restriction = await get_time_restrictions_by_user_type(user_id, type)
    if time_restriction:
        await time_restriction.delete()


async def set_time_restriction_alert(user_id: int, type: str):
    time_restriction = await get_time_restrictions_by_user_type(user_id, type)
    if time_restriction:
        await time_restriction.update(alerted=True).apply()


async def add_flag(name: str):
    await models.Flag.create(name=name)


async def get_flag(name: str):
    if flag := await models.Flag.get(name):
        return flag.value
    return None


async def remove_flag(name: str):
    flag = await get_flag(name)
    if flag:
        await flag.delete()


async def set_flag(name: str, value: bool):
    flag = await get_flag(name)
    if flag:
        await flag.update(value=value).apply()


async def add_softban(user_id: int, issuer_id: int, reason: str):
    await add_dbmember_if_not_exist(user_id)
    await models.Softban.create(id=generate_id(), user=user_id, issuer=issuer_id, reason=reason)


async def remove_softban(user_id: int):
    softban = await get_softban(user_id)
    if softban:
        await softban.delete()


async def add_dbmember(user_id: int):
    return await models.Member.create(id=user_id)


async def add_dbmember_if_not_exist(user_id: int):
    db_member = await get_dbmember(user_id)
    if not db_member:
        db_member = await add_dbmember(user_id)
    return db_member


async def get_dbmember(user_id: int):
    return await models.Member.get(user_id)


async def add_dbchannel(channel_id: int, name: str):
    return await models.Channel.create(id=channel_id, name=name)


async def get_dbchannel(channel_id: int):
    return await models.Channel.get(channel_id)


async def add_dbrole(role_id: int, name: str):
    return await models.Role.create(id=role_id, name=name)


async def get_dbrole(role_id: int):
    return await models.Role.get(role_id)


async def get_softban(user_id: int):
    return await models.Softban.query.where(models.Softban.user == user_id).gino.first()


async def add_watch(user_id: int):
    db_member = await add_dbmember_if_not_exist(user_id)
    await db_member.update(watched=True).apply()


async def remove_watch(user_id: int):
    db_member = await get_dbmember(user_id)
    if db_member:
        await db_member.update(watched=False).apply()


async def is_watched(user_id: int):
    db_member = await get_dbmember(user_id)
    return db_member.watched if db_member else False


async def add_nofilter(channel: TextChannel):
    db_channel = await get_dbchannel(channel.id)
    if not db_channel:
        db_channel = await add_dbchannel(channel.id, channel.name)
    await db_channel.update(nofilter=True).apply()


async def remove_nofilter(channel: TextChannel):
    db_channel = await get_dbchannel(channel.id)
    if db_channel:
        await db_channel.update(nofilter=True).apply()


async def check_nofilter(channel: TextChannel):
    channel = await models.Channel.get(channel.id)
    return channel.nofilter if channel else False


async def add_friendcode(user_id: int, fc: int):
    await add_dbmember_if_not_exist(user_id)
    await models.FriendCode.create(id=user_id, fc_3ds=fc)


async def get_friendcode(user_id: int):
    return await models.FriendCode.get(user_id)


async def delete_friendcode(user_id: int):
    friendcode = await get_friendcode(user_id)
    if friendcode:
        await friendcode.delete()
