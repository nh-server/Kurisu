from discord.ext import commands
import re


class SafeMember(commands.Converter):
    # A re-implementation of https://github.com/Rapptz/discord.py/blob/1863a1c6636f53592519320a173ec9573c090c0b/discord/ext/commands/converter.py
    def convert(self):
        message = self.ctx.message
        match = re.match(r'([0-9]{15,21})$', self.argument) or re.match(r'<@!?([0-9]+)>$', self.argument)
        server = message.server
        result = None
        if match is None:
            # not a mention...
            if server and "#" in self.argument:
                result = server.get_member_named(self.argument)
                if result is None:
                    raise commands.errors.BadArgument('Member "{}" not found. Search terms are case sensitive.'.format(self.argument))
            else:
                raise commands.errors.BadArgument('Matches by only nick/username are not allowed.')
        else:
            user_id = match.group(1)
            if server:
                result = server.get_member(user_id)
            if result is None:
                raise commands.errors.BadArgument('Member "{}" not found.'.format(user_id))

        return result