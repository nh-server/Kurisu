import discord

from discord.ext import commands
from utils import crud
from utils.utils import send_dm_message


class Logs(commands.Cog):
    """
    Logs join and leave messages, bans and unbans, and member changes.
    """

    def __init__(self, bot):
        self.bot = bot

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

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_all_ready()
        self.logo_nitro = discord.utils.get(self.bot.guild.emojis, name="nitro") or "⁉"
        self.logo_boost = discord.utils.get(self.bot.guild.emojis, name="boost") or "⁉"
        self.nitro_msg = f"""Thanks for boosting {self.logo_nitro} Nintendo Homebrew!
        As a Nitro Booster you have the following bonuses:
        - React permissions in {self.bot.channels['off-topic'].mention}, {self.bot.channels['elsewhere'].mention}, and {self.bot.channels['nintendo-discussion'].mention}.
        - Able to use the `.nickme` command in DMs with Kurisu to change your nickname every 6 hours.
        - Able to stream in the {self.bot.channels['streaming-gamer'].mention} voice channel.
        Thanks for boosting and have a good time! {self.logo_boost}
        """

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.wait_until_all_ready()
        msg = f"✅ **Join**: {member.mention} | {self.bot.escape_text(member)}\n🗓 __Creation__: {member.created_at}\n🏷 __User ID__: {member.id}"
        softban = await crud.get_softban(member.id)
        if softban:
            message_sent = await send_dm_message(member, f"This account has not been permitted to participate in {self.bot.guild.name}. The reason is: {softban.reason}")
            self.bot.actions.append("sbk:" + str(member.id))
            await member.kick()
            msg = f"🚨 **Attempted join**: {member.mention} is soft-banned by <@{softban.issuer}> | {self.bot.escape_text(member)}"
            if not message_sent:
                msg += "\nThis message did not send to the user."
            embed = discord.Embed(color=discord.Color.red())
            embed.description = softban.reason
            await self.bot.channels['server-logs'].send(msg, embed=embed)
            return
        perm_roles = await crud.get_permanent_roles(member.id)
        if perm_roles:
            roles = [member.guild.get_role(perm_role.id) for perm_role in perm_roles]
            await member.add_roles(*roles)

        warns = await crud.get_warns(member.id)
        if len(warns) == 0:
            await self.bot.channels['server-logs'].send(msg)
        else:
            embed = discord.Embed(color=discord.Color.dark_red())
            embed.set_author(name=f"Warns for {member}", icon_url=member.avatar_url)
            for idx, warn in enumerate(warns):
                embed.add_field(name=f"{idx + 1}: {discord.utils.snowflake_time(warn.id).strftime('%Y-%m-%d %H:%M:%S')}", value=f"Issuer: {self.bot.escape_text((await self.bot.fetch_user(warn.issuer)).display_name)}\nReason: {warn.reason}")
            await self.bot.channels['server-logs'].send(msg, embed=embed)
        await send_dm_message(member, self.welcome_msg.format(member.name, member.guild.name, self.bot.channels['welcome-and-rules'].mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.bot.wait_until_all_ready()
        if "uk:" + str(member.id) in self.bot.actions:
            self.bot.actions.remove("uk:" + str(member.id))
            return
        if "sbk:" + str(member.id) in self.bot.actions:
            self.bot.actions.remove("sbk:" + str(member.id))
            return
        if self.bot.pruning != 0 and "wk:" + str(member.id) not in self.bot.actions:
            self.bot.pruning -= 1
            if self.bot.pruning == 0:
                await self.bot.channels['mods'].send("Pruning finished!")
            return
        msg = f"{'👢 **Auto-kick**' if 'wk:' + str(member.id) in self.bot.actions else '⬅️ **Leave**'}: {member.mention} | {self.bot.escape_text(member)}\n🏷 __User ID__: {member.id}"
        await self.bot.channels['server-logs'].send(msg)
        if "wk:" + str(member.id) in self.bot.actions:
            self.bot.actions.remove("wk:" + str(member.id))
            await self.bot.channels['mod-logs'].send(msg)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        await self.bot.wait_until_all_ready()
        ban = await guild.fetch_ban(member)
        auto_ban = 'wb:' + str(member.id) in self.bot.actions
        if "ub:" + str(member.id) in self.bot.actions:
            self.bot.actions.remove("ub:" + str(member.id))
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
    async def on_member_unban(self, guild, user):
        await self.bot.wait_until_all_ready()
        if "tbr:" + str(user.id) in self.bot.actions:
            self.bot.actions.remove("tbr:" + str(user.id))
            return
        msg = f"⚠️ **Unban**: {user.mention} | {self.bot.escape_text(user)}"
        if await crud.get_time_restriction_by_user_type(user.id, 'timeban'):
            msg += "\nTimeban removed."
            await crud.remove_timed_restriction(user.id, 'timeban')
        await self.bot.channels['mod-logs'].send(msg)

    @commands.Cog.listener()
    async def on_member_update(self, member_before, member_after):
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
                if self.bot.roles["Nitro Booster"] in diff:
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
        if do_log:
            msg = f"ℹ️ **Member update**: {member_after.mention} | {self.bot.escape_text(member_after)} {msg}"
            await dest.send(msg)

    @commands.Cog.listener()
    async def on_user_update(self, member_before, member_after):
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


def setup(bot):
    bot.add_cog(Logs(bot))
