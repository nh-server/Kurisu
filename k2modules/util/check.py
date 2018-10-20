from discord.ext import commands

# some of this is from Luc#5653's help, who got it from RoboDanny


def check_for_position(*, helper=False, staff=False, op=False, superop=False, owner=False):
    """Check if the user has a certain position."""
    async def predicate(ctx: commands.Context):
        valid = True
        roles = ctx.author.roles
        get_role = ctx.bot.get_role_by_name
        # maybe need to think of a better way to do this...
        if helper:
            valid = valid and (await get_role('helpers-role')) in roles
        if staff:
            valid = valid and (await get_role('staff-role')) in roles
        if op:
            valid = valid and ((await get_role('op-role')) in roles
                               or (await get_role('superop-role')) in roles
                               or (await get_role('owner-role')) in roles)
        if superop:
            valid = valid and ((await get_role('superop-role')) in roles
                               or (await get_role('owner-role')) in roles)
        if owner:
            valid = valid and (await get_role('owner-role')) in roles
        return valid

    return commands.check(predicate)
