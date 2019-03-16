from discord.ext import commands
import re


class SafeMember(commands.Converter):
    # A re-implementation of https://github.com/Rapptz/discord.py/blob/1863a1c6636f53592519320a173ec9573c090c0b/discord/ext/commands/converter.py
    async def convert(self, ctx, argument):
        message = ctx.message
        match = re.match(r'([0-9]{15,21})$', argument) or re.match(r'<@!?([0-9]+)>$', argument)
        guild = ctx.guild
        if match is None:
            # not a mention...
            if guild and "#" in argument:
                result = guild.get_member_named(argument)
                if result is None:
                    raise commands.errors.BadArgument('Member "{}" not found. Search terms are case sensitive.'.format(argument))
            else:
                raise commands.errors.BadArgument('Matches by only nick/username are not allowed.')
        else:
            user_id = int(match.group(1))
            result = guild.get_member(user_id)
            if result is None:
                raise commands.errors.BadArgument('Member "{}" not found.'.format(user_id))
        return result
