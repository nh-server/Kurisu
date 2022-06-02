from __future__ import annotations

import discord
import logging

from discord.ext import commands
from inspect import cleandoc
from os.path import dirname, join
from typing import Optional, Literal, TYPE_CHECKING
from utils import crud
from utils.models import Channel
from utils.views import BasePaginator, PaginatedEmbedView
from utils.checks import check_if_user_can_sr, is_staff
from utils.mdcmd import add_md_files_as_commands

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


class Assistance(commands.Cog, command_attrs=dict(cooldown=commands.CooldownMapping.from_cooldown(1, 30.0, commands.BucketType.channel))):
    """
    Commands that will mostly be used in the help channels.
    """

    format_map = {
        'nx_firmware': '14.1.1',
        'ams_ver': '1.3.1',
        'hekate_ver': '5.7.2',
        'last_revision': 'April 19th, 2022',
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

    async def setup_assistance(self):
        await self.bot.wait_until_all_ready()
        self.emoji = discord.utils.get(self.bot.guild.emojis, name='3dslogo') or discord.PartialEmoji.from_str("⁉")
        channel_id = await Channel.query.where(Channel.name == 'small-help').gino.scalar()
        if channel_id:
            channel = self.bot.guild.get_channel(channel_id)
            if channel and channel.type == discord.ChannelType.category:
                self.small_help_category = channel

    async def unisearch(self, query: str) -> list[dict]:
        query = query.lower()
        res = {}
        async with self.bot.session.get('https://udb-api.lightsage.dev/search/' + query, timeout=45) as r:
            if r.status == 200:
                j = await r.json()
                res = j['results']
        return res

    async def simple_embed(self, ctx: commands.Context, text: str, *, title: str = "", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = cleandoc(text)
        await ctx.send(embed=embed)

    @check_if_user_can_sr()
    @commands.guild_only()
    @commands.command(aliases=["sr"], cooldown=None)
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
    @commands.command(cooldown=None)
    async def createsmallhelp(self, ctx: GuildContext, console: Literal['3ds', 'switch', 'wiiu', 'legacy'], helpee: discord.Member, desc: str):
        """Creates a small help channel with the option to add a member. Helper+ only."""
        if not self.small_help_category:
            return await ctx.send("The small help category is not set.")
        channel = await self.small_help_category.create_text_channel(name=f"{console}-{helpee.name}-{desc}")
        await helpee.add_roles(self.bot.roles['Small Help'])
        await channel.send(f"{helpee.mention}, come here for help.")
        await self.bot.channels['mod-logs'].send(f"⭕️ **Small help access granted**: {ctx.author.mention} granted access to small help channel to {helpee.mention}")
        msg = f"🆕 **Small help channel created**: {ctx.author.mention} created small help channel {channel.mention} | {channel.name} ({channel.id})"
        await self.bot.channels['mod-logs'].send(msg)
        await ctx.send(f"Created small help {channel.mention}.")

    @is_staff('OP')
    @commands.guild_only()
    @commands.command(cooldown=None)
    async def setsmallhelp(self, ctx: GuildContext, category: discord.CategoryChannel):
        """Sets the small help category for creating channels. OP+ only."""
        if dbchannel := await Channel.query.where(Channel.name == 'small-help').gino.one_or_none():
            await dbchannel.update(id=category.id).apply()
        else:
            await crud.add_dbchannel(category.id, name='small-help')
        self.small_help_category = category
        await ctx.send("Small help category set.")

    @commands.command()
    async def nxcfw(self, ctx: KurisuContext, cfw=""):
        """Information on why we don't support or recommend various other Switch CFWs"""

        if cfw == "sx":  # Alias for sxos
            cfw = "sxos"

        cfwinfo = {
            'kosmos': {
                'info': """
                        * Kosmos bundles several extras, including system modules which can cause issues with booting if they are not compatible
                        with the currently running firmware. As a result, troubleshooting is often required to figure out which one is causing the issue.""",
                'title': "Kosmos"
            },
            'reinx': {
                'info': """
                        * Older versions have caused bans due to the incorrectly implemented user agent string.
                        * The author has expressed no interest in adding emuMMC/emuNAND.
                        * The author has expressed that they feel it doesn't matter if consoles get banned.
                        * It often takes weeks to several months for it to get support for the latest firmware.""",
                'title': "ReiNX"
            },
            'sxos': {
                'info': """
                        * SX OS is illegal to purchase and own. It bundles various keys and copyrighted data that cannot be legally shared.
                        * It has known compatibility issues with homebrew, due to its non-standard and proprietary nature.
                        * It does not support loading custom system modules.
                        * Several versions of the CFW have caused users to be banned without their knowledge.""",
                'title': "SX OS"
            }
        }

        if not (info := cfwinfo.get(cfw)):
            await ctx.send(f"Please specify a cfw. Valid options are: {', '.join([x for x in cfwinfo])}.")

            ctx.command.reset_cooldown(ctx)
            return
        await self.simple_embed(ctx, info['info'], title=f"Why {info['title']} isn't recommended")

    @commands.command()
    async def luma(self, ctx: KurisuContext, lumaversion=""):
        """Download links for Luma versions"""
        if len(lumaversion) >= 3 and lumaversion[0].isdigit() and lumaversion[1] == "." and lumaversion[2].isdigit():
            await self.simple_embed(ctx, f"Luma v{lumaversion}\nhttps://github.com/LumaTeam/Luma3DS/releases/tag/v{lumaversion}", color=discord.Color.blue())
        elif lumaversion == "latest":
            await self.simple_embed(ctx, "Latest Luma Version:\nhttps://github.com/LumaTeam/Luma3DS/releases/latest", color=discord.Color.blue())
        else:
            await self.simple_embed(ctx, """
                                    Download links for the most common Luma3DS releases:
                                    [Latest Luma](https://github.com/LumaTeam/Luma3DS/releases/latest)
                                    [Luma v7.0.5](https://github.com/LumaTeam/Luma3DS/releases/tag/v7.0.5)
                                    [Luma v7.1](https://github.com/LumaTeam/Luma3DS/releases/tag/v7.1)
                                    """, color=discord.Color.blue())

    @commands.group(cooldown=commands.CooldownMapping.from_cooldown(0, 0, commands.BucketType.channel), invoke_without_command=True, case_insensitive=True)
    async def tutorial(self, ctx: KurisuContext):
        """Links to one of multiple guides"""
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send_help(ctx.command)
        else:
            await ctx.send(f'{ctx.author.mention}, if you wish to view the \
complete list of tutorials, send `.tutorial` to me in a DM.', delete_after=10)

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def invite(self, ctx: KurisuContext, name: str = ""):
        """Post an invite to an approved server"""
        if not name:
            ctx.command.reset_cooldown(ctx)
            if self.bot.invitefilter.invites:
                return await ctx.send(f"Valid server names are: {', '.join(x.alias for x in self.bot.invitefilter.invites)}")
            else:
                return await ctx.send("There is no approved servers!")

        invite = await self.bot.invitefilter.fetch_invite_by_alias(alias=name)

        if invite:
            await ctx.send(f"https://discord.gg/{invite.code}")
            if invite.is_temporary:
                if invite.uses > 1:
                    await self.bot.invitefilter.set_uses(code=invite.code, uses=invite.uses - 1)
                else:
                    await self.bot.invitefilter.delete(code=invite.code)
        else:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"Invalid invite name. Valid server names are: {', '.join(x.alias for x in self.bot.invitefilter.invites)}")

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


add_md_files_as_commands(Assistance)
add_md_files_as_commands(Assistance, join(Assistance.data_dir, 'tutorial'), namespace=Assistance.tutorial)  # type: ignore


async def setup(bot):
    await bot.add_cog(Assistance(bot))
