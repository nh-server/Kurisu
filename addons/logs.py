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

    welcome_msg = """
Hello {0}, welcome to the {1} server on Discord!

Please review all of the rules in {2} before asking for help or chatting. In particular, we do not allow assistance relating to piracy.

You can find a list of staff and helpers in {2}.

Do you simply need a place to start hacking your 3DS system? Check out **<https://3ds.guide>**!
Do you simply need a place to start hacking your Wii U system? Check out **<https://wiiu.guide/>**!

By participating in this server, you acknowledge that user data (including messages, user IDs, user tags) will be collected and logged for moderation purposes. If you disagree with this collection, please leave the server immediately.

Thanks for stopping by and have a good time!
"""  # ughhhhhhhh

    async def on_member_join(self, member):
        await self.bot.wait_until_all_ready()
        msg = "✅ **Join**: {} | {}#{}\n🗓 __Creation__: {}\n🏷 __User ID__: {}".format(
            member.mention, self.bot.escape_name(member.name), member.discriminator, member.created_at, member.id
        )
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        if member.id in softbans:
            message_sent = False
            try:
                await self.bot.send_message(member, "This account has not been permitted to participate in {}. The reason is: {}".format(self.bot.server.name, softbans[member.id]["reason"]))
                message_sent = True
            except discord.errors.Forbidden:
                pass
            self.bot.actions.append("sbk:"+member.id)
            await self.bot.kick(member)
            msg = "🚨 **Attempted join**: {} is soft-banned by <@{}> | {}#{}".format(member.mention, softbans[member.id]["issuer_id"], self.bot.escape_name(member.name), member.discriminator)
            if not message_sent:
                msg += "\nThis message did not send to the user."
            embed = discord.Embed(color=discord.Color.red())
            embed.description = softbans[member.id]["reason"]
            await self.bot.send_message(self.bot.serverlogs_channel, msg, embed=embed)
            return
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id in rsts:
            roles = []
            for rst in rsts[member.id]:
                roles.append(discord.utils.get(self.bot.server.roles, name=rst))
            await self.bot.add_roles(member, *roles)
        with open("data/warns.json", "r") as f:
            warns = json.load(f)
        # crappy workaround given how dicts are not ordered
        try:
            warn_count = len(warns[member.id]["warns"])
            if warn_count == 0:
                await self.bot.send_message(self.bot.serverlogs_channel, msg)
            else:
                embed = discord.Embed(color=discord.Color.dark_red())
                embed.set_author(name="Warns for {}#{}".format(self.bot.escape_name(member.name), member.discriminator), icon_url=member.avatar_url)
                for key in range(warn_count):
                    warn = warns[member.id]["warns"][str(key + 1)]
                    embed.add_field(name="{}: {}".format(key + 1, warn["timestamp"]), value="Issuer: {}\nReason: {}".format(warn["issuer_name"], warn["reason"]))
                await self.bot.send_message(self.bot.serverlogs_channel, msg, embed=embed)
        except KeyError:  # if the user is not in the file
            await self.bot.send_message(self.bot.serverlogs_channel, msg)
        try:
            await self.bot.send_message(member, self.welcome_msg.format(self.bot.escape_name(member.name), self.bot.server.name, self.bot.welcome_channel.mention))
        except discord.errors.Forbidden:
            pass

    async def on_member_remove(self, member):
        await self.bot.wait_until_all_ready()
        if "uk:"+member.id in self.bot.actions:
            self.bot.actions.remove("uk:"+member.id)
            return
        if "sbk:"+member.id in self.bot.actions:
            self.bot.actions.remove("sbk:"+member.id)
            return
        if self.bot.pruning != 0 and "wk:"+member.id not in self.bot.actions:
            self.bot.pruning -= 1
            if self.bot.pruning == 0:
                await self.bot.send_message(self.bot.mods_channel, "Pruning finished!")
            return
        msg = "{}: {} | {}#{}\n🏷 __User ID__: {}".format("👢 **Auto-kick**" if "wk:"+member.id in self.bot.actions else "⬅️ **Leave**", member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        await self.bot.send_message(self.bot.serverlogs_channel, msg)
        if "wk:"+member.id in self.bot.actions:
            self.bot.actions.remove("wk:"+member.id)
            await self.bot.send_message(self.bot.modlogs_channel, msg)

    async def on_member_ban(self, member):
        await self.bot.wait_until_all_ready()
        if "ub:"+member.id in self.bot.actions:
            self.bot.actions.remove("ub:"+member.id)
            return
        msg = "⛔ **{}**: {} | {}#{}\n🏷 __User ID__: {}".format("Auto-ban" if "wb:"+member.id in self.bot.actions else "Ban", member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        await self.bot.send_message(self.bot.serverlogs_channel, msg)
        if "wb:"+member.id in self.bot.actions:
            self.bot.actions.remove("wb:"+member.id)
        else:
            msg += "\nThe responsible staff member should add an explanation below."
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    async def on_member_unban(self, server, user):
        await self.bot.wait_until_all_ready()
        if "tbr:"+user.id in self.bot.actions:
            self.bot.actions.remove("tbr:"+user.id)
            return
        msg = "⚠️ **Unban**: {} | {}#{}".format(user.mention, self.bot.escape_name(user.name), user.discriminator)
        if user.id in self.bot.timebans:
            msg += "\nTimeban removed."
            self.bot.timebans.pop(user.id)
            with open("data/timebans.json", "r") as f:
                timebans = json.load(f)
            if user.id in timebans:
                timebans.pop(user.id)
                with open("data/timebans.json", "w") as f:
                    json.dump(timebans, f)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    async def on_member_update(self, member_before, member_after):
        await self.bot.wait_until_all_ready()
        do_log = False  # only nickname and roles should be logged
        dest = self.bot.modlogs_channel
        if member_before.roles != member_after.roles:
            do_log = True
            dest = self.bot.serverlogs_channel
            # role removal
            if len(member_before.roles) > len(member_after.roles):
                msg = "\n👑 __Role removal__: "
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
                msg = "\n👑 __Role addition__: "
                for index, role in enumerate(member_after.roles):
                    if role.name == "@everyone":
                        continue
                    if role not in member_before.roles:
                        msg += "__**" + role.name + "**__"
                    else:
                        msg += role.name
                    if index != len(member_after.roles) - 1:
                        msg += ", "
        if self.bot.escape_name(member_before.name) != self.bot.escape_name(member_after.name):
            do_log = True
            dest = self.bot.serverlogs_channel
            msg = "\n📝 __Username change__: {} → {}".format(self.bot.escape_name(member_before.name), self.bot.escape_name(member_after.name))
        if member_before.nick != member_after.nick:
            do_log = True
            if member_before.nick == None:
                msg = "\n🏷 __Nickname addition__"
            elif member_after.nick == None:
                msg = "\n🏷 __Nickname removal__"
            else:
                msg = "\n🏷 __Nickname change__"
            msg += ": {0} → {1}".format(self.bot.escape_name(member_before.nick), self.bot.escape_name(member_after.nick))
        if do_log:
            msg = "ℹ️ **Member update**: {} | {}#{}".format(member_after.mention, self.bot.escape_name(member_after.name), member_after.discriminator) + msg
            await self.bot.send_message(dest, msg)

def setup(bot):
    bot.add_cog(Logs(bot))
