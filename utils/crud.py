import datetime

from . import models
from discord import TextChannel, utils
from typing import Optional


def generate_id() -> int:
    return utils.time_snowflake(datetime.datetime.now())


async def add_permanent_role(user_id: int, role_id: int) -> Optional[models.PermanentRole]:
    await add_dbmember_if_not_exist(user_id)
    if not await models.PermanentRole.query.where((models.PermanentRole.user_id == user_id) & (
            models.PermanentRole.role_id == role_id)).gino.first():
        return await models.PermanentRole.create(user_id=user_id, role_id=role_id)


async def remove_permanent_role(user_id: int, role_id: int) -> Optional[models.PermanentRole]:
    permanent_role = await models.PermanentRole.query.where((models.PermanentRole.user_id == user_id) & (
            models.PermanentRole.role_id == role_id)).gino.first()
    if permanent_role:
        await permanent_role.delete()
        return permanent_role


async def get_permanent_roles(user_id: int) -> list[models.PermanentRole]:
    return await models.Role.query.where((models.Role.id == models.PermanentRole.role_id) & (models.PermanentRole.user_id == user_id)).gino.all()


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


async def get_staff_all() -> list[models.Staff]:
    return await models.Staff.query.where(models.Staff.position != 'Helper').gino.all()


async def get_staff(user_id: int) -> Optional[models.Staff]:
    return await models.Staff.query.where(
        (models.Staff.position != 'Helper') & (models.Staff.id == user_id)).gino.first()


async def get_helpers() -> list[models.Staff]:
    return await models.Staff.query.where(models.Staff.console.isnot(None)).gino.all()


async def get_helper(user_id: int) -> Optional[models.Staff]:
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


async def get_warn(warn_id: int) -> Optional[models.Warn]:
    return await models.Warn.get(warn_id)


async def get_warns(user_id: int) -> list[models.Warn]:
    return await models.Warn.query.where(models.Warn.user == user_id).gino.all()


async def remove_warn_id(user_id: int, index: int):
    warn = await models.Warn.query.where(models.Warn.user == user_id).offset(index - 1).gino.first()
    await warn.delete()


async def remove_warns(user_id: int) -> int:
    n_warns = await (models.db.select([models.db.func.count()]).where(models.Warn.user == user_id).gino.scalar())
    if n_warns:
        await models.Warn.delete.where(models.Warn.user == user_id).gino.status()
    return n_warns


async def add_timed_restriction(user_id: int, end_date: datetime.datetime, restriction_type: str):
    await add_dbmember_if_not_exist(user_id)
    await models.TimedRestriction.create(id=generate_id(), user=user_id, type=restriction_type,
                                         end_date=end_date)


async def get_time_restrictions_by_user(user_id: int) -> list[models.TimedRestriction]:
    return await models.TimedRestriction.query.where(models.TimedRestriction.user == user_id).gino.all()


async def get_time_restriction_by_user_type(user_id: int, restriction_type: str) -> models.TimedRestriction:
    return await models.TimedRestriction.query.where((models.TimedRestriction.user == user_id) & (
            models.TimedRestriction.type == restriction_type)).gino.first()


async def get_time_restrictions_by_type(restriction_type: str) -> list[models.TimedRestriction]:
    return await models.TimedRestriction.query.where(models.TimedRestriction.type == restriction_type).gino.all()


async def remove_timed_restriction(user_id: int, restriction_type: str):
    time_restriction = await get_time_restriction_by_user_type(user_id, restriction_type)
    if time_restriction:
        await time_restriction.delete()


async def set_time_restriction_alert(user_id: int, restriction_type: str):
    time_restriction = await get_time_restriction_by_user_type(user_id, restriction_type)
    if time_restriction:
        await time_restriction.update(alerted=True).apply()


async def add_timed_role(user_id: int, role_id: int, expiring_date: datetime.datetime) -> models.TimedRole:
    await add_dbmember_if_not_exist(user_id)
    entry = await get_timed_role_by_user_type(user_id, role_id)
    if not entry:
        return await models.TimedRole.create(id=generate_id(), user_id=user_id, role_id=role_id, expiring_date=expiring_date)
    await entry.update(expiring_date=expiring_date).apply()
    return entry


async def remove_timed_role(user_id: int, role_id: int):
    timed_role = await get_timed_role_by_user_type(user_id, role_id)
    if timed_role:
        await timed_role.delete()


async def get_timed_role_by_user_type(user_id: int, role_id: int) -> Optional[models.TimedRole]:
    return await models.TimedRole.query.where(
        (models.TimedRole.user_id == user_id) & (models.TimedRole.role_id == role_id)).gino.first()


async def get_timed_roles() -> list[models.TimedRole]:
    return await models.TimedRole.query.gino.all()


async def add_flag(name: str):
    await models.Flag.create(name=name)


async def get_flag(name: str) -> Optional[models.Flag]:
    return await models.Flag.get(name)


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


async def get_softban(user_id: int) -> Optional[models.Softban]:
    return await models.Softban.query.where(models.Softban.user == user_id).gino.first()


async def remove_softban(user_id: int):
    softban = await get_softban(user_id)
    if softban:
        await softban.delete()


async def add_dbmember(user_id: int):
    return await models.Member.create(id=user_id)


async def add_dbmember_if_not_exist(user_id: int) -> models.Member:
    db_member = await get_dbmember(user_id)
    if not db_member:
        db_member = await add_dbmember(user_id)
    return db_member


async def get_dbmember(user_id: int) -> Optional[models.Member]:
    return await models.Member.get(user_id)


async def add_dbchannel(channel_id: int, name: str):
    return await models.Channel.create(id=channel_id, name=name)


async def get_dbchannel(channel_id: int) -> Optional[models.Channel]:
    return await models.Channel.get(channel_id)


async def add_dbrole(role_id: int, name: str):
    return await models.Role.create(id=role_id, name=name)


async def get_dbrole(role_id: int) -> Optional[models.Channel]:
    return await models.Role.get(role_id)


async def add_watch(user_id: int):
    db_member = await add_dbmember_if_not_exist(user_id)
    await db_member.update(watched=True).apply()


async def remove_watch(user_id: int):
    db_member = await get_dbmember(user_id)
    if db_member:
        await db_member.update(watched=False).apply()


async def is_watched(user_id: int) -> bool:
    db_member = await get_dbmember(user_id)
    return db_member.watched if db_member else False


async def get_watch_list() -> list[models.Member]:
    return await models.Member.query.where(models.Member.watched == True).gino.all()  # noqa: E712


async def add_nofilter(channel: TextChannel):
    db_channel = await get_dbchannel(channel.id)
    if not db_channel:
        db_channel = await add_dbchannel(channel.id, channel.name)
    await db_channel.update(nofilter=True).apply()


async def remove_nofilter(channel: TextChannel):
    db_channel = await get_dbchannel(channel.id)
    if db_channel:
        await db_channel.update(nofilter=False).apply()


async def check_nofilter(channel: TextChannel) -> bool:
    channel = await models.Channel.get(channel.id)
    return channel.nofilter if channel else False


async def add_friendcode_3ds(user_id: int, fc: int):
    await add_dbmember_if_not_exist(user_id)
    if fcs := await get_friendcode(user_id):
        await fcs.update(fc_3ds=fc).apply()
        return
    await models.FriendCode.create(id=user_id, fc_3ds=fc)


async def add_friendcode_switch(user_id: int, fc: int):
    await add_dbmember_if_not_exist(user_id)
    if fcs := await get_friendcode(user_id):
        await fcs.update(fc_switch=fc).apply()
        return
    await models.FriendCode.create(id=user_id, fc_switch=fc)


async def get_friendcode(user_id: int) -> Optional[models.FriendCode]:
    return await models.FriendCode.get(user_id)


async def delete_friendcode_3ds(user_id: int):
    friendcodes = await get_friendcode(user_id)
    if friendcodes:
        await friendcodes.update(fc_3ds=None).apply()
        if friendcodes.fc_3ds is None and friendcodes.fc_switch is None:
            await friendcodes.delete()


async def delete_friendcode_switch(user_id: int):
    friendcodes = await get_friendcode(user_id)
    if friendcodes:
        await friendcodes.update(fc_switch=None).apply()
        if friendcodes.fc_3ds is None and friendcodes.fc_switch is None:
            await friendcodes.delete()


async def add_rule(number: int, description: str):
    rule = await get_rule(number)
    if not rule:
        await models.Rule.create(id=number, description=description)


async def edit_rule(number: int, description: str):
    rule = await get_rule(number)
    if rule:
        await rule.update(description=description).apply()


async def delete_rule(number: int):
    rule = await get_rule(number)
    if rule:
        await rule.delete()


async def get_rules() -> list[models.Rule]:
    return await models.Rule.query.order_by(models.Rule.id).gino.all()


async def get_rule(number: int) -> Optional[models.Rule]:
    return await models.Rule.get(number)


async def add_reminder(date: datetime.datetime, author: int, reminder: str):
    await add_dbmember_if_not_exist(author)
    await models.RemindMeEntry.create(id=generate_id(), date=date, author=author, reminder=reminder)


async def get_reminders() -> list[models.RemindMeEntry]:
    return await models.RemindMeEntry.query.order_by(models.RemindMeEntry.date).gino.all()


async def remove_reminder(reminder_id: int):
    db_reminder = await models.RemindMeEntry.get(reminder_id)
    await db_reminder.delete()


async def create_tag(title: str, content: str, author: int):
    await add_dbmember_if_not_exist(author)
    await models.Tag.create(id=generate_id(), title=title, content=content, author=author)


async def get_tag(title: str) -> Optional[models.Tag]:
    return await models.Tag.query.where(models.Tag.title == title).gino.first()


async def get_tags() -> list[models.Tag]:
    return await models.Tag.query.order_by(models.Tag.id).gino.all()


async def search_tags(query: str) -> list[models.Tag]:
    return await models.Tag.query.where(models.Tag.title.ilike(f"%{query}%")).limit(10).gino.all()


async def delete_tag(title: str):
    db_tag = await get_tag(title)
    await db_tag.delete()


async def add_citizen(citizen_id):
    await add_dbmember_if_not_exist(citizen_id)
    return await models.Citizen.create(id=citizen_id, social_credit=100)


async def get_citizen(citizen_id: int) -> Optional[models.Citizen]:
    return await models.Citizen.get(citizen_id)


async def add_citizen_if_not_exist(citizen_id: int) -> models.Citizen:
    return await get_citizen(citizen_id) or await add_citizen(citizen_id)


async def add_social_credit(citizen_id: int, social_credit: int):
    citizen = await add_citizen_if_not_exist(citizen_id)
    await citizen.update(social_credit=citizen.social_credit + social_credit).apply()


async def remove_citizen(citizen_id):
    citizen = await get_citizen(citizen_id)
    await citizen.delete()
