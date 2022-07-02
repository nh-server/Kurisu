from __future__ import annotations

import discord

from discord.ext import commands
from discord.utils import format_dt
from typing import TYPE_CHECKING
from utils.utils import send_dm_message
from utils import Restriction

if TYPE_CHECKING:
    from kurisu import Kurisu


class Logs(commands.Cog):
    """
    Logs join and leave messages, bans and unbans, and member changes.
    """

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.bot.loop.create_task(self.init_rules())
        self.restrictions = self.bot.restrictions
        self.warns = self.bot.warns

    welcome_msg = """
Hello {0}, welcome to the {1} server on Discord!

Please review all of the rules in {2} before asking for help or chatting. In particular, we do not allow assistance relating to piracy.

You can find a list of staff and helpers in {2}.

Do you simply need a place to start hacking your 3DS system? Check out **<https://3ds.hacks.guide>**!
Do you simply need a place to start hacking your Wii U system? Check out **<https://wiiu.hacks.guide>**!
Do you simply need a place to start hacking your Switch system? Check out **<https://nh-server.github.io/switch-guide/>**!

By participating in this server, you acknowledge that user data (including messages, user IDs, user tags) will be collected and logged for moderation purposes. If you disagree with this collection, please leave the server immediately.

Thanks for stopping by and have a good time!
"""  # ughhhhhhhh

    async def init_rules(self):
        await self.bot.wait_until_all_ready()
        self.logo_nitro = discord.utils.get(self.bot.guild.emojis, name="nitro") or discord.PartialEmoji.from_str("⁉")
        self.logo_boost = discord.utils.get(self.bot.guild.emojis, name="boost") or discord.PartialEmoji.from_str("⁉")
        self.nitro_msg = (
            f"Thanks for boosting {self.logo_nitro} Nintendo Homebrew!\n"
            f"As a Nitro Booster you have the following bonuses:\n"
            f"- React permissions in {self.bot.channels['off-topic'].mention}, {self.bot.channels['elsewhere'].mention},"
            f" and {self.bot.channels['nintendo-discussion'].mention}.\n"
            f"- Able to use the `.nickme` command in DMs with Kurisu to change your nickname every 6 hours.\n"
            f"- Able to stream in the {self.bot.channels['streaming-gamer'].mention} voice channel.\n"
            f"Thanks for boosting and have a good time! {self.logo_boost}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot.wait_until_all_ready()
        msg = f"✅ **Join**: {member.mention} | {self.bot.escape_text(member)}\n🗓 __Creation__: {member.created_at}\n🏷 __User ID__: {member.id}"
        if member.id in self.restrictions.softbans:
            softban = self.restrictions.softbans[member.id]
            message_sent = await send_dm_message(member, f"This account has not been permitted to participate in {self.bot.guild.name}."
                                                         f" The reason is: {softban.reason}")
            self.bot.actions.append("sbk:" + str(member.id))
            await member.kick()
            msg = f"🚨 **Attempted join**: {member.mention} is soft-banned by <@{softban.issuer_id}> | {self.bot.escape_text(member)}"
            if not message_sent:
                msg += "\nThis message did not send to the user."
            embed = discord.Embed(color=discord.Color.red())
            embed.description = softban.reason
            await self.bot.channels['server-logs'].send(msg, embed=embed)
            return
        roles = []
        async for r in self.restrictions.get_restrictions_by_user(member.id):
            restriction = Restriction[r[2]]
            role = self.bot.roles.get(restriction.value)
            if role:
                roles.append(role)
        if roles:
            await member.add_roles(*roles)

        warns = [w async for w in self.warns.get_warnings(member)]

        if not warns:
            await self.bot.channels['server-logs'].send(msg)
        else:
            embed = discord.Embed(color=discord.Color.dark_red())
            embed.set_author(name=f"Warns for {member}", icon_url=member.display_avatar.url)
            for idx, warn in enumerate(warns):
                name = member.guild.get_member(warn.issuer_id) or f"ID {warn.issuer_id}"
                embed.add_field(name=f"{idx + 1}: {warn.date:%Y-%m-%d %H:%M:%S}", value=f"Issuer: {name}\nReason: {warn.reason}")
            await self.bot.channels['server-logs'].send(msg, embed=embed)
        if not self.bot.configuration.auto_probation:
            await send_dm_message(member, self.welcome_msg.format(member.name, member.guild.name, self.bot.channels['welcome-and-rules'].mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.bot.wait_until_all_ready()
        if self.bot.pruning is True:
            return
        if "uk:" + str(member.id) in self.bot.actions:
            self.bot.actions.remove("uk:" + str(member.id))
            return
        if "sbk:" + str(member.id) in self.bot.actions:
            self.bot.actions.remove("sbk:" + str(member.id))
            return
        msg = f"{'👢 **Auto-kick**' if 'wk:' + str(member.id) in self.bot.actions else '⬅️ **Leave**'}: {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}"
        await self.bot.channels['server-logs'].send(msg)
        if "wk:" + str(member.id) in self.bot.actions:
            self.bot.actions.remove("wk:" + str(member.id))
            await self.bot.channels['mod-logs'].send(msg)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        await self.bot.wait_until_all_ready()
        ban = await guild.fetch_ban(member)
        auto_ban = f'wb:{member.id}' in self.bot.actions
        if f"ub:{member.id}" in self.bot.actions:
            self.bot.actions.remove(f'ub:{member.id}')
            return
        msg = f"{'⛔ **Auto-ban**' if auto_ban else '⛔ **Ban**'}: {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}"
        if ban.reason:
            msg += "\n✏️ __Reason__: " + ban.reason
        if auto_ban:
            self.bot.actions.remove("wb:" + str(member.id))
            await self.bot.channels['mods'].send(msg)
        await self.bot.channels['server-logs'].send(msg)
        if not ban.reason:
            msg += "\nThe responsible staff member should add an explanation below."
        await self.bot.channels['mod-logs'].send(msg)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        await self.bot.wait_until_all_ready()
        if f'bu:{user.id}' in self.bot.actions:
            self.bot.actions.remove(f'bu:{user.id}')
            return
        msg = f"⚠️ **Unban**: {user.mention} | {self.bot.escape_text(user)}"
        if discord.utils.get(self.restrictions.timed_restricions, user_id=user.id, type=Restriction.Ban.value):
            msg += "\nTimeban removed."
            await self.restrictions.remove_restriction(user, Restriction.Ban)
        await self.bot.channels['mod-logs'].send(msg)

    @commands.Cog.listener()
    async def on_member_update(self, member_before: discord.Member, member_after: discord.Member):
        await self.bot.wait_until_all_ready()
        do_log = False  # only nickname and roles should be logged
        dest = self.bot.channels['server-logs']
        roles_before = set(member_before.roles)
        roles_after = set(member_after.roles)
        msg = ""
        if roles_before ^ roles_after:
            do_log = True
            # role removal
            if roles_before - roles_after:
                msg = "\n👑 __Role removal__: "
                roles = []
                for role in roles_before:
                    if role.name == "@everyone":
                        continue
                    role_name = self.bot.escape_text(role.name)
                    if role not in roles_after:
                        roles.append("_~~" + role_name + "~~_")
                    else:
                        roles.append(role_name)
                msg += ', '.join(roles)
            # role addition
            elif diff := roles_after - roles_before:
                msg = "\n👑 __Role addition__: "
                roles = []
                if member_before.guild.premium_subscriber_role in diff:
                    try:
                        await member_after.send(self.nitro_msg)
                    except discord.Forbidden:
                        pass
                for role in roles_after:
                    if role.name == "@everyone":
                        continue
                    role_name = self.bot.escape_text(role.name)
                    if role not in roles_before:
                        roles.append("__**" + role_name + "**__")
                    else:
                        roles.append(role_name)
                msg += ', '.join(roles)
        if member_before.nick != member_after.nick:
            do_log = True
            if member_before.nick is None:
                msg = "\n🏷 __Nickname addition__"
            elif member_after.nick is None:
                msg = "\n🏷 __Nickname removal__"
            else:
                msg = "\n🏷 __Nickname change__"
            msg += f": {self.bot.escape_text(member_before.nick)} → {self.bot.escape_text(member_after.nick)}"
        if member_before.timed_out_until != member_after.timed_out_until:
            do_log = True
            if member_before.timed_out_until is None:
                msg = "\n🚷 __Timeout addition__"
            elif member_after.timed_out_until is None:
                msg = "\n🚷 __Timeout removal__"
            else:
                msg = "\n🚷 __Timeout change__"
            timeout_before = format_dt(member_before.timed_out_until) if member_before.timed_out_until else 'None'
            timeout_after = format_dt(member_after.timed_out_until) if member_after.timed_out_until else 'None'
            msg += f": {timeout_before} → {timeout_after}"
        if do_log:
            msg = f"ℹ️ **Member update**: {member_after.mention} | {self.bot.escape_text(member_after)} {msg}"
            await dest.send(msg)

    @commands.Cog.listener()
    async def on_user_update(self, member_before: discord.Member, member_after: discord.Member):
        await self.bot.wait_until_all_ready()
        do_log = False  # only usernames and discriminators should be logged
        dest = self.bot.channels['server-logs']
        msg = ""
        if member_before.name != member_after.name:
            do_log = True
            msg = f"\n📝 __Username change__: {self.bot.escape_text(member_before.name)} → {self.bot.escape_text(member_after.name)}"
        elif member_before.discriminator != member_after.discriminator:
            do_log = True
            msg = f"\n🔢 __Discriminator change__: {self.bot.escape_text(member_before)} → {self.bot.escape_text(member_after)}"
        if do_log:
            msg = f"ℹ️ **Member update**: {member_after.mention} | {self.bot.escape_text(member_after)} {msg}"
            await dest.send(msg)


async def setup(bot):
    await bot.add_cog(Logs(bot))
