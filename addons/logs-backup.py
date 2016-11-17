import logging
import discord
from discord.ext import commands
from sys import argv

log = logging.getLogger('discord')

class Logs:
    """
    Logs join and leave messages, bans and unbans, and member changes.
    """
    def __init__(self, bot):
        self.bot = bot
    print('Addon "Logs" has been loaded.')

    async def on_member_join(self, member):
        server = member.server
        msg = "✅ **Join**: {0} | {1}#{2}\n🗓 __Creation__: {3}".format(
            member.mention, member.name, member.discriminator, member.created_at
        )
        await self.bot.send_message(discord.utils.get(server.channels, name="server-logs"), msg)

    async def on_member_remove(self, member):
        server = member.server
        msg = "⬅️ **Leave**: {0} | {1}#{2}".format(member.mention, member.name, member.discriminator)
        await self.bot.send_message(discord.utils.get(server.channels, name="server-logs"), msg)

    async def on_member_ban(self, member):
        server = member.server
        msg = "⛔ **Ban**: {0} | {1}#{2}".format(member.mention, member.name, member.discriminator)
        await self.bot.send_message(discord.utils.get(server.channels, name="server-logs"), msg)
        await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg + "\nThe responsible staff member should add an explanation below.")

    async def on_member_unban(self, server, user):
        msg = "⚠️ **Unban**: {0} | {1}#{2}".format(user.mention, user.name, user.discriminator)
        await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)

    async def on_member_update(self, member_before, member_after):
        do_log = False  # only nickname and roles should be logged
        server = member_after.server
        msg = "ℹ️ **Member update**: {0} | {1}#{2}".format(member_after.mention, member_after.name, member_after.discriminator)
        if member_before.roles != member_after.roles:
            do_log = True
            # role removal
            if len(member_before.roles) > len(member_after.roles):
                msg += "\n👑 __Role removal__: "
                for index, role in enumerate(member_before.roles):
                    if role.name == "@everyone":
                        continue
                    if role not in member_after.roles:
                        msg += "_~~" + role.name + "~~_"
                    else:
                        msg += role.name
                    if index != len(member_before.roles) - 1:
                        msg += ", "
            # role addition
            elif len(member_before.roles) < len(member_after.roles):
                msg += "\n👑 __Role addition__: "
                for index, role in enumerate(member_after.roles):
                    if role.name == "@everyone":
                        continue
                    if role not in member_before.roles:
                        msg += "__**" + role.name + "**__"
                    else:
                        msg += role.name
                    if index != len(member_after.roles) - 1:
                        msg += ", "
        if member_before.name != member_after.name:
            do_log = True
            msg += "\n📝 __Username change__: {0} → {1}".format(member_before.name, member_after.name)
        if member_before.nick != member_after.nick:
            do_log = True
            if member_before.nick == None:
                msg += "\n🏷 __Nickname addition__"
            elif member_after.nick == None:
                msg += "\n🏷 __Nickname removal__"
            else:
                msg += "\n🏷 __Nickname change__"
            msg += ": {0} → {1}".format(member_before.nick, member_after.nick)
        if do_log:
            await self.bot.send_message(discord.utils.get(server.channels, name="mod-logs"), msg)

def setup(bot):
    bot.add_cog(Logs(bot))
