import discord
from discord.ext import commands
import json


class Logs(commands.Cog):
    """
    Logs join and leave messages, bans and unbans, and member changes.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Cog "{}" loaded'.format(self.__class__.__name__))

    welcome_msg = """
Hello {0}, welcome to the {1} server on Discord!

Please review all of the rules in {2} before asking for help or chatting. In particular, we do not allow assistance relating to piracy.

You can find a list of staff and helpers in {2}.

Do you simply need a place to start hacking your 3DS system? Check out **<https://3ds.hacks.guide>**!
Do you simply need a place to start hacking your Wii U system? Check out **<https://wiiu.hacks.guide/>**!

By participating in this server, you acknowledge that user data (including messages, user IDs, user tags) will be collected and logged for moderation purposes. If you disagree with this collection, please leave the server immediately.

Thanks for stopping by and have a good time!
"""  # ughhhhhhhh

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.wait_until_all_ready()
        msg = "✅ **Join**: {} | {}#{}\n🗓 __Creation__: {}\n🏷 __User ID__: {}".format(
            member.mention, self.bot.escape_name(member.name), member.discriminator, member.created_at, member.id
        )
        softbans = [x[0] for x in self.bot.c.execute('SELECT user_id from softbans').fetchall()]
        if member.id in softbans:
            message_sent = False
            try:
                await member.send("This account has not been permitted to participate in {}. The reason is: {}".format(self.bot.server.name, softbans[member.id]["reason"]))
                message_sent = True
            except discord.errors.Forbidden:
                pass
            self.bot.actions.append("sbk:"+str(member.id))
            await member.kick()
            msg = "🚨 **Attempted join**: {} is soft-banned by <@{}> | {}#{}".format(member.mention, softbans[member.id]["issuer_id"], self.bot.escape_name(member.name), member.discriminator)
            if not message_sent:
                msg += "\nThis message did not send to the user."
            embed = discord.Embed(color=discord.Color.red())
            embed.description = softbans[member.id]["reason"]
            await self.bot.serverlogs_channel.send(msg, embed=embed)
            return
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id in self.bot.timemutes:
            self.bot.add_roles(member, self.bot.muted_role)
        if member.id in rsts:
            roles = []
            for rst in rsts[member.id]:
                roles.append(await member.guild.roles.get(name=rst))
            await member.add_roles(*roles)
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        try:
            if len(warns[member.id]["warns"]) == 0:
                await self.bot.serverlogs_channel.send(msg)
            else:
                embed = discord.Embed(color=discord.Color.dark_red())
                embed.set_author(name="Warns for {}#{}".format(self.bot.escape_name(member.name), member.discriminator), icon_url=member.avatar_url)
                for idx, warn in enumerate(warns[member.id]["warns"]):
                    embed.add_field(name="{}: {}".format(idx + 1, warn["timestamp"]), value="Issuer: {}\nReason: {}".format(warn["issuer_name"], warn["reason"]))
                await self.bot.serverlogs_channel.send(msg, embed=embed)
        except KeyError:  # if the user is not in the file
            await self.bot.serverlogs_channel.send(msg)
        try:
            await member.send(self.welcome_msg.format(self.bot.escape_name(member.name), member.guild.name, self.bot.welcome_channel.mention))
        except discord.errors.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.bot.wait_until_all_ready()
        if "uk:"+str(member.id) in self.bot.actions:
            self.bot.actions.remove("uk:"+str(member.id))
            return
        if "sbk:"+str(member.id) in self.bot.actions:
            self.bot.actions.remove("sbk:"+str(member.id))
            return
        if self.bot.pruning != 0 and "wk:"+str(member.id) not in self.bot.actions:
            self.bot.pruning -= 1
            if self.bot.pruning == 0:
                await self.bot.mods_channel.send("Pruning finished!")
            return
        msg = "{}: {} | {}#{}\n🏷 __User ID__: {}".format("👢 **Auto-kick**" if "wk:"+str(member.id) in self.bot.actions else "⬅️ **Leave**", member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        await self.bot.serverlogs_channel.send(msg)
        if "wk:"+str(member.id) in self.bot.actions:
            self.bot.actions.remove("wk:"+str(member.id))
            await self.bot.modlogs_channel.send(msg)

    @commands.Cog.listener()
    async def on_member_ban(self, member):
        await self.bot.wait_until_all_ready()
        if "ub:"+member.id in self.bot.actions:
            self.bot.actions.remove("ub:"+str(member.id))
            return
        msg = "⛔ **{}**: {} | {}#{}\n🏷 __User ID__: {}".format("Auto-ban" if "wb:"+member.id in self.bot.actions else "Ban", member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
        await self.bot.serverlogs_channel.send(msg)
        if "wb:"+member.id in self.bot.actions:
            self.bot.actions.remove("wb:"+str(member.id))
        else:
            msg += "\nThe responsible staff member should add an explanation below."
        await self.bot.modlogs_channel.send(msg)

    @commands.Cog.listener()
    async def on_member_unban(self, server, user):
        await self.bot.wait_until_all_ready()
        if "tbr:"+str(user.id) in self.bot.actions:
            self.bot.actions.remove("tbr:"+str(user.id))
            return
        msg = "⚠️ **Unban**: {} | {}#{}".format(user.mention, self.bot.escape_name(user.name), user.discriminator)
        if user.id in self.bot.timebans:
            msg += "\nTimeban removed."
            self.bot.timebans.popstr(user.id)
            self.bot.execute('DELETE FROM timed_restriction WHERE user_id=? and type="timeban"',user.id)
        await self.bot.modlogs_channel.send(msg)

    @commands.Cog.listener()
    async def on_member_update(self, member_before, member_after):
        await self.bot.wait_until_all_ready()
        do_log = False  # only nickname and roles should be logged
        dest = self.bot.modlogs_channel
        roles_before = set(member_before.roles)
        roles_after = set(member_after.roles)
        if roles_before ^ roles_after:
            do_log = True
            dest = self.bot.serverlogs_channel
            # role removal
            if roles_before - roles_after:
                msg = "\n👑 __Role removal__: "
                roles = []
                for role in roles_before:
                    if role.name == "@everyone":
                        continue
                    if role not in roles_after:
                        roles.append("_~~" + role.name + "~~_")
                    else:
                        roles.append(role.name)
                msg += ', '.join(roles)
            # role addition
            elif roles_after - roles_before:
                msg = "\n👑 __Role addition__: "
                roles = []
                for role in roles_after:
                    if role.name == "@everyone":
                        continue
                    if role not in roles_before:
                        roles.append("__**" + role.name + "**__")
                    else:
                        roles.append(role.name)
                msg += ', '.join(roles)
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
            await dest.send(msg)

def setup(bot):
    bot.add_cog(Logs(bot))
