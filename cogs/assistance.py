from __future__ import annotations

import discord
import logging

from discord.ext import commands
from inspect import cleandoc
from os.path import dirname, join
from typing import Optional, Literal, TYPE_CHECKING
from utils.checks import check_if_user_can_sr, is_staff
from utils.mdcmd import add_md_files_as_commands
from utils.views import BasePaginator, PaginatedEmbedView
from utils.utils import KurisuCooldown

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext, GuildContext

logger = logging.getLogger(__name__)


class UniDBResultsPaginator(BasePaginator):
    def __init__(self, results: list[dict]):
        super().__init__(n_pages=len(results))
        self.results = results

    def current(self):
        if embed := self.pages.get(self.idx):
            return embed
        else:
            embed = self.create_embed(app=self.results[self.idx])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, app: dict):
        embed = discord.Embed(color=int(app['color'][1:], 16))
        embed.title = app['title']
        embed.description = f"{app.get('description', 'No description provided.')}\n"
        if 'download_page' in app:
            embed.description += f" [[Download]({app['download_page']})]"
        elif 'nightly' in app and 'download_page' in app['nightly']:
            embed.description += f" [[Download]({app['nightly']['download_page']})]"
        if 'source' in app:
            embed.description += f" [[Source]({app['source']})]"
        embed.set_footer(text=f"by {app['author']}")
        embed.set_thumbnail(url=app["image"])

        if qr_urls := app.get('qr'):
            embed.set_image(url=list(qr_urls.values())[0])

        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"

        return embed


class Assistance(commands.GroupCog):
    """
    Commands that will mostly be used in the help channels.
    """

    format_map = {
        'nx_firmware': '16.0.0',
        'ams_ver': '1.5.0',
        'hekate_ver': '6.0.2',
        'last_revision': 'February 23rd, 2023',
    }

    # compatibility until the use of these variables is removed
    nx_firmware = format_map['nx_firmware']
    ams_ver = format_map['ams_ver']
    hekate_ver = format_map['hekate_ver']
    last_revision = format_map['last_revision']

    data_dir = join(dirname(__file__), 'assistance-cmds')

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.small_help_category: Optional[discord.CategoryChannel] = None
        self.bot.loop.create_task(self.setup_assistance())
        self.filters = bot.filters

    async def setup_assistance(self):
        await self.bot.wait_until_all_ready()
        self.emoji = discord.utils.get(self.bot.guild.emojis, name='3dslogo') or discord.PartialEmoji.from_str("⁉")
        db_channel = await self.bot.configuration.get_channel_by_name('small-help')
        if db_channel:
            channel = self.bot.guild.get_channel(db_channel[0])
            if channel and channel.type == discord.ChannelType.category:
                self.small_help_category = channel

    async def unisearch(self, query: str) -> list[dict]:
        query = query.lower()
        res = []
        async with self.bot.session.get('https://udb-api.lightsage.dev/search/' + query, timeout=45) as r:
            if r.status == 200:
                j = await r.json()
                res = j['results']
        return res

    async def simple_embed(self, ctx: commands.Context, text: str, *, title: str = "", color=discord.Color.default()):
        mention_author = any(ctx.message.mentions)
        embed = discord.Embed(title=title, color=color)
        embed.description = cleandoc(text)
        await ctx.send(embed=embed, reference=ctx.message.reference, mention_author=mention_author)

    @check_if_user_can_sr()
    @commands.guild_only()
    @commands.command(aliases=["sr"])
    async def staffreq(self, ctx: GuildContext, *, msg_request: str = ""):
        """Request staff, with optional additional text. Trusted, Helpers, Staff, Retired Staff, Verified only."""
        author = ctx.author
        await ctx.message.delete()
        msg = f"❗️ **Assistance requested**: {ctx.channel.mention} by {author.mention} | {self.bot.escape_text(author)} @here"
        if msg_request != "":
            embed = discord.Embed(color=discord.Color.gold())
            embed.description = msg_request
        else:
            embed = None
        await self.bot.channels['mods'].send(msg, embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))  # type: ignore
        try:
            await author.send(f"✅ Online staff have been notified of your request in {ctx.channel.mention}.", embed=embed)  # type: ignore
        except discord.errors.Forbidden:
            pass

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command()
    async def createsmallhelp(self, ctx: GuildContext, console: Literal['3ds', 'switch', 'wiiu', 'legacy'], helpee: discord.Member, *, desc: str):
        """Creates a small help channel for a user. Helper+ only."""
        if not self.small_help_category:
            return await ctx.send("The small help category is not set.")
        # Channel names can't be longer than 100 characters
        channel_name = f"{console}-{helpee.name}-{desc}"[:100]
        channel = await self.small_help_category.create_text_channel(name=channel_name)
        await channel.set_permissions(helpee, read_messages=True)
        await channel.send(f"{helpee.mention}, come here for help.")
        await self.bot.channels['mod-logs'].send(f"⭕️ **Small help access granted**: {ctx.author.mention} granted access to small help channel to {helpee.mention}")
        msg = f"🆕 **Small help channel created**: {ctx.author.mention} created small help channel {channel.mention} | {channel.name} ({channel.id})"
        await self.bot.channels['mod-logs'].send(msg)
        await ctx.send(f"Created small help {channel.mention}.")

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command()
    async def createsoap(self, ctx: GuildContext, helpee: discord.Member, *):
        """Creates a small help channel for a user. Helper+ only."""
        if not self.small_help_category:
            return await ctx.send("The small help category is not set.")
        # Channel names can't be longer than 100 characters
        channel_name = f"3ds-{helpee.name}-soap"[:100]
        channel = await self.small_help_category.create_text_channel(name=channel_name)
        await channel.set_permissions(helpee, read_messages=True)
        await channel.send(f"{helpee.mention}, please read the following.\n"
                            "0. If your console is on, turn it off. If your console happens to already be in GodMode9, skip to step 3.\n"
                            "1. Insert your SD card into your console\n"
                            "2. Boot into GodMode9 by holding start while powering on\n"
                            "3. Navigate to SysNAND Virtual\n"
                            "4. Select essential.exefs\n"
                            "5. Select copy to 0:/gm9/out\n"
                            "6. Power off your console and insert your SD card into your computer\n"
                            "7. Navigate to /gm9/out on your SD, essential.exefs should be there\n"
                            "8. Send the essential.exefs in this specific channel\n"
                            " - Please do not send it anywhere else.\n"
                            " - File contains very sensitive console unique certificates.\n"
                            " - These allow impersonation of console in servers, do not publicly share it.\n"
                            "9. Find your serial number label under your console and provide the text written or a picture of it\n"
                            " - On a New 2DS, this is located under the game card and sdcard slot cover\n"
                            " - If you can't locate your serial number or the label is missing/rubbed off:\n"
                            "  - For New 3DS not XL/LL, it should be under the top plate\n"
                            "  - Other models, under the bottom plate there should be a copy of your label or under the battery\n"
                            "  - If you still can't find it, please request further assistance\n"
                            "10. Please wait for further instructions.")
        await self.bot.channels['mod-logs'].send(f"⭕️ **Soap access granted**: {ctx.author.mention} granted access to soap channel to {helpee.mention}")
        msg = f"🆕 **Soap channel created**: {ctx.author.mention} created soap channel {channel.mention} | {channel.name} ({channel.id})"
        await self.bot.channels['mod-logs'].send(msg)
        await ctx.send(f"Created soap {channel.mention}.")

    @is_staff('OP')
    @commands.guild_only()
    @commands.command()
    async def setsmallhelp(self, ctx: GuildContext, category: discord.CategoryChannel):
        """Sets the small help category for creating channels. OP+ only."""
        await self.bot.configuration.add_channel('small-help', category)
        self.small_help_category = category
        await ctx.send("Small help category set.")

    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    @commands.command()
    async def nxcfw(self, ctx: KurisuContext, cfw=""):
        """Information on why we don't support or recommend various other Switch CFWs"""

        if cfw == "sx":  # Alias for sxos
            cfw = "sxos"

        cfwinfo = {
            'kosmos': {
                'info':
                    ('* Kosmos bundles several extras, including system modules which can cause issues'
                     ' with booting if they are not compatible with the currently running firmware. '
                     'As a result, troubleshooting is often required to figure out which one is causing the issue.'),
                'title': "Kosmos"
            },
            'reinx': {
                'info':
                    ('* Older versions have caused bans due to the incorrectly implemented user agent string.'
                     '* The author has expressed no interest in adding emuMMC/emuNAND.'
                     '* The author has expressed that they feel it doesn\'t matter if consoles get banned.'
                     '* It often takes weeks to several months for it to get support for the latest firmware.'),
                'title': "ReiNX"
            },
            'sxos': {
                'info':
                    ('* SX OS is illegal to purchase and own. It bundles various keys and copyrighted data that cannot be legally shared.'
                     '* It has known compatibility issues with homebrew, due to its non-standard and proprietary nature.'
                     '* It does not support loading custom system modules.'
                     '* Several versions of the CFW have caused users to be banned without their knowledge.'),
                'title': "SX OS"
            }
        }

        if not (info := cfwinfo.get(cfw)):
            await ctx.send(f"Please specify a cfw. Valid options are: {', '.join(x for x in cfwinfo)}.")

            ctx.command.reset_cooldown(ctx)
            return
        await self.simple_embed(ctx, info['info'], title=f"Why {info['title']} isn't recommended")

    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    @commands.command()
    async def luma(self, ctx: KurisuContext, lumaversion=""):
        """Download links for Luma versions"""
        if len(lumaversion) >= 3 and lumaversion[0].isdigit() and lumaversion[1] == "." and lumaversion[2].isdigit():
            await self.simple_embed(ctx, f"Luma v{lumaversion}\nhttps://github.com/LumaTeam/Luma3DS/releases/tag/v{lumaversion}", color=discord.Color.blue())
        elif lumaversion == "latest":
            await self.simple_embed(ctx, "Latest Luma Version:\nhttps://github.com/LumaTeam/Luma3DS/releases/latest", color=discord.Color.blue())
        else:
            await self.simple_embed(ctx,
                                    "Download links for the most common Luma3DS releases:\n"
                                    "[Latest Luma](https://github.com/LumaTeam/Luma3DS/releases/latest)\n"
                                    "[Luma v7.0.5](https://github.com/LumaTeam/Luma3DS/releases/tag/v7.0.5)\n"
                                    "[Luma v7.1](https://github.com/LumaTeam/Luma3DS/releases/tag/v7.1)",
                                    color=discord.Color.blue())

    @commands.group(cooldown=None, invoke_without_command=True, case_insensitive=True)
    async def tutorial(self, ctx: KurisuContext):
        """Links to one of multiple guides"""
        if isinstance(ctx.channel, discord.DMChannel) or ctx.channel == self.bot.channels['bot-cmds']:
            await ctx.send_help(ctx.command)
        else:
            await ctx.send(f'{ctx.author.mention}, if you wish to view the '
                           f'complete list of tutorials, send `.help tutorial` to me in a {self.bot.channels["bot-cmds"]}.',
                           delete_after=10)

    @commands.dynamic_cooldown(KurisuCooldown(1, 5.0), commands.BucketType.channel)
    @commands.command()
    async def invite(self, ctx: KurisuContext, name: str = ""):
        """Post a discord invite to an approved server"""
        if not name:
            ctx.command.reset_cooldown(ctx)
            if self.filters.approved_invites:
                return await ctx.send(f"Valid server names are: {', '.join(ai.alias for ai in self.filters.approved_invites.values())}")
            else:
                return await ctx.send("There is no approved servers!")

        invite = self.filters.get_invite_named(name)

        if invite:
            await ctx.send(f"https://discord.gg/{invite.code}")
            if invite.uses != -1:
                if invite.uses > 1:
                    await self.filters.update_invite_use(invite.code)
                else:
                    await self.filters.delete_approved_invite(invite.code)
        else:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"Invalid invite name. Valid server names are: {', '.join(ai.alias for ai in self.filters.approved_invites.values())}")

    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    @commands.command()
    async def unidb(self, ctx: KurisuContext, *, query=""):
        """Links to Universal-DB and/or one of the apps.\n
        To link to Universal-DB: `unidb`
        To search for an app: `unidb [query]`"""
        if query == "":
            embed = discord.Embed(title="Universal-DB")
            embed.set_author(name="Universal-Team")
            embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/49733679?s=400&v=4")
            embed.description = "A database of DS and 3DS homebrew"
            embed.url = "https://db.universal-team.net/"
            embed.colour = discord.Color.from_rgb(7, 47, 79)
            return await ctx.send(embed=embed)
        res = await self.unisearch(query)
        if not res:
            return await ctx.send("No app found!")
        view = PaginatedEmbedView(paginator=UniDBResultsPaginator(res), author=ctx.author)
        view.message = await ctx.send(embed=view.paginator.current(), view=view)

    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    @commands.hybrid_command()
    async def mkey(self, ctx: KurisuContext, device: Literal['3ds', 'dsi', 'wii', 'wiiu', 'switch'], month: commands.Range[int, 1, 12], day: commands.Range[int, 1, 31], inquiry: str, device_id: Optional[str] = None):
        """
        Generate a master key for resetting parental control for given device.
        Usage: `mkey <3ds|dsi|wii|wiiu|switch> <month> <day> <inquiry (no space)> <deviceid (switch 8.0+ only)>`

        Args:
            device: Your console model.
            month: The system's month.
            day: The console's day.
            inquiry: Your inquiry number.
            device_id: Your device id. Only required on switch 8.0+.
        """

        device_codes = {
            "3ds": "CTR",
            "dsi": "TWL",
            "wii": "RVL",
            "wiiu": "WUP",
            "switch": "HAC"
        }

        device_code = device_codes[device]

        if device_id and not ctx.interaction:
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
        api_call = f"https://mkey.eiphax.tech/api?platform={device_code}&inquiry={inquiry}&month={month}&day={day}"
        if device_id:
            api_call += f"&aux={device_id}"
        async with self.bot.session.get(api_call) as r:
            if r.status == 200:
                ret = await r.json()
                return await ctx.send(f'{ctx.author.mention if not ctx.interaction else ""} Your key is {ret["key"]}.', ephemeral=True)
            else:
                return await ctx.send(f'{ctx.author.mention if not ctx.interaction else ""} API returned error {r.status}. Please check your values and try again.', ephemeral=True)

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command(hidden=True)
    async def dev(self, ctx: KurisuContext):
        """Reminds user where they are. Helper+ only"""
        await ctx.message.delete()
        await ctx.send(f"You {'do not ' if ctx.channel != self.bot.channels['dev'] else ''}seem to be in {self.bot.channels['dev'].mention}.")

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command(hidden=True)
    async def meta(self, ctx: KurisuContext):
        """Reminds user where they are. (2) Helper+ only"""
        await ctx.message.delete()
        await ctx.send(f"You {'do not ' if ctx.channel != self.bot.channels['meta'] else ''}seem to be in {self.bot.channels['meta'].mention}. Please take this subject {'there' if ctx.channel != self.bot.channels['meta'] else 'somewhere else'}.")

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command(hidden=True)
    async def appeals(self, ctx: KurisuContext):
        """Reminds user where they are. (3) Helper+ only"""
        await ctx.message.delete()
        await ctx.send(f"You {'do not ' if ctx.channel != self.bot.channels['appeals'] else ''}seem to be in {self.bot.channels['appeals'].mention}. Please take this subject {'there' if ctx.channel != self.bot.channels['appeals'] else 'somewhere else'}.")

    @is_staff('Helper')
    @commands.guild_only()
    @commands.command(hidden=True)
    async def ot(self, ctx: KurisuContext):
        """Reminds user where they are. (4) Helper+ only"""
        await ctx.message.delete()
        await ctx.send(f"You {'do not ' if ctx.channel != self.bot.channels['off-topic'] else ''}seem to be in {self.bot.channels['off-topic'].mention}. Please take this subject {'there' if ctx.channel != self.bot.channels['off-topic'] else 'somewhere else'}.")


add_md_files_as_commands(Assistance)
add_md_files_as_commands(Assistance, join(Assistance.data_dir, 'tutorial'), namespace=Assistance.tutorial)  # type: ignore


async def setup(bot):
    await bot.add_cog(Assistance(bot))
