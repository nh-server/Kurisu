import discord
import json
from discord.ext import commands
from sys import argv

class Logs:
    """
    Logs join and leave messages, bans and unbans, and member changes.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def on_member_join(self, member):
        await self.bot.wait_until_ready()
        msg = "✅ **Join**: {} | {}#{}\n🗓 __Creation__: {}\n🏷 __User ID__: {}".format(
            member.mention, member.name, member.discriminator, member.created_at, member.id
        )
        with open("restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id in rsts:
            roles = []
            for rst in rsts[member.id]:
                roles.append(discord.utils.get(self.bot.server.roles, name=rst))
            await self.bot.add_roles(member, *roles)
        with open("warns.json", "r") as f:
            warns = json.load(f)
        # crappy workaround given how dicts are not ordered
        try:
            warn_count = len(warns[member.id]["warns"])
            if warn_count == 0:
                await self.bot.send_message(self.bot.serverlogs_channel, msg)
            else:
                embed = discord.Embed(color=discord.Color.dark_red())
                embed.set_author(name="Warns for {}#{}".format(member.display_name, member.discriminator), icon_url=member.avatar_url)
                for key in range(warn_count):
                    warn = warns[member.id]["warns"][str(key + 1)]
                    embed.add_field(name="{}: {}".format(key + 1, warn["timestamp"]), value="Issuer: {}\nReason: {}".format(warn["issuer_name"], warn["reason"]))
                await self.bot.send_message(self.bot.serverlogs_channel, msg, embed=embed)
        except KeyError:  # if the user is not in the file
            await self.bot.send_message(self.bot.serverlogs_channel, msg)
        try:
            await self.bot.send_message(member, "Hello {0}, welcome to the {1} server on Discord!\n\nPlease review all of the rules in {2} before asking for help or chatting. In particular, we do not allow assistance relating to piracy.\n\nYou can find a list of staff and helpers in {2}.\n\nDo you simply need a place to start hacking your 3DS system? Check out **<https://3ds.guide>**!\n\nThanks for stopping by and have a good time!".format(member.name, self.bot.server.name, self.bot.welcome_channel.mention))
        except discord.errors.Forbidden:
            pass

    async def on_member_remove(self, member):
        await self.bot.wait_until_ready()
        if "uk:"+member.id in self.bot.actions:
            self.bot.actions.remove("uk:"+member.id)
            return
        msg = "{}: {} | {}#{}\n🏷 __User ID__: {}".format("👢 **Auto-kick**" if "wk:"+member.id in self.bot.actions else "⬅️ **Leave**", member.mention, member.name, member.discriminator, member.id)
        await self.bot.send_message(self.bot.serverlogs_channel, msg)
        if "wk:"+member.id in self.bot.actions:
            self.bot.actions.remove("wk:"+member.id)
            await self.bot.send_message(self.bot.modlogs_channel, msg)

    async def on_member_ban(self, member):
        await self.bot.wait_until_ready()
        if "ub:"+member.id in self.bot.actions:
            self.bot.actions.remove("ub:"+member.id)
            return
        msg = "⛔ **{}**: {} | {}#{}\n🏷 __User ID__: {}".format("Auto-ban" if "wb:"+member.id in self.bot.actions else "Ban", member.mention, member.name, member.discriminator, member.id)
        await self.bot.send_message(self.bot.serverlogs_channel, msg)
        if "wb:"+member.id in self.bot.actions:
            self.bot.actions.remove("wb:"+member.id)
        else:
            msg += "\nThe responsible staff member should add an explanation below."
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    async def on_member_unban(self, server, user):
        await self.bot.wait_until_ready()
        msg = "⚠️ **Unban**: {} | {}#{}".format(user.mention, user.name, user.discriminator)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    async def on_member_update(self, member_before, member_after):
        await self.bot.wait_until_ready()
        do_log = False  # only nickname and roles should be logged
        dest = self.bot.modlogs_channel
        msg = "ℹ️ **Member update**: {} | {}#{}".format(member_after.mention, member_after.name, member_after.discriminator)
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
            dest = self.bot.serverlogs_channel
            msg += "\n📝 __Username change__: {} → {}".format(member_before.name, member_after.name)
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
            await self.bot.send_message(dest, msg)

def setup(bot):
    bot.add_cog(Logs(bot))
