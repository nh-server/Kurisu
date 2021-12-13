import discord
import logging

from discord.ext import commands
from inspect import cleandoc
from os.path import dirname, join

from utils.utils import PaginatedEmbedView
from utils.checks import check_if_user_can_sr
from utils.mdcmd import add_md_files_as_commands

logger = logging.getLogger(__name__)


class Assistance(commands.Cog, command_attrs=dict(cooldown=commands.CooldownMapping.from_cooldown(1, 30.0, commands.BucketType.channel))):
    """
    Commands that will mostly be used in the help channels.
    """

    format_map = {
        'nx_firmware': '13.2.0',
        'ams_ver': '1.2.4',
        'hekate_ver': '5.6.5',
        'last_revision': 'December 1st, 2021',
    }

    # compatibility until the use of these variables is removed
    nx_firmware = format_map['nx_firmware']
    ams_ver = format_map['ams_ver']
    hekate_ver = format_map['hekate_ver']
    last_revision = format_map['last_revision']

    data_dir = join(dirname(__file__), 'assistance-cmds')

    def __init__(self, bot):
        self.bot = bot

    async def unisearch(self, query: str) -> list[dict]:
        query = query.lower()
        res = {}
        async with self.bot.session.get('https://udb-api.lightsage.dev/search/' + query, timeout=45) as r:
            if r.status == 200:
                j = await r.json()
                res = j['results']
        return res

    async def simple_embed(self, ctx, text, *, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = cleandoc(text)
        await ctx.send(embed=embed)

    @check_if_user_can_sr()
    @commands.guild_only()
    @commands.command(aliases=["sr"], cooldown=commands.CooldownMapping.from_cooldown(rate=0, per=0, type=commands.BucketType.channel))
    async def staffreq(self, ctx, *, msg_request: str = ""):
        """Request staff, with optional additional text. Trusted, Helpers, Staff, Retired Staff, Verified only."""
        author = ctx.author
        await ctx.message.delete()
        msg = f"❗️ **Assistance requested**: {ctx.channel.mention} by {author.mention} | {self.bot.escape_text(author)} @here"
        if msg_request != "":
            embed = discord.Embed(color=discord.Color.gold())
            embed.description = msg_request
        else:
            embed = None
        await self.bot.channels['mods'].send(msg, embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))
        try:
            await author.send(f"✅ Online staff have been notified of your request in {ctx.channel.mention}.", embed=(embed if msg_request != "" else None))
        except discord.errors.Forbidden:
            pass

    @commands.command()
    async def nxcfw(self, ctx, cfw=""):
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
    async def luma(self, ctx, lumaversion=""):
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
    async def tutorial(self, ctx):
        """Links to one of multiple guides"""
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send_help(ctx.command)
        else:
            await ctx.send(f'{ctx.author.mention}, if you wish to view the \
complete list of tutorials, send `.tutorial` to me in a DM.', delete_after=10)

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def invite(self, ctx, name: str = ""):
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

    @commands.guild_only()
    @commands.command()
    async def unidb(self, ctx, *, query=""):
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

        embeds = []
        for app in res:
            embed = discord.Embed(title=app['title'], color=int(app['color'][1:], 16))
            embed.description = f"{app.get('description', '')}\n [[Download]({app['download_page']})]"
            if 'source' in app:
                embed.description += f" [[Source]({app['source']})]"
            embed.set_footer(text=f"by {app['author']}")
            embed.set_thumbnail(url=app["image"])
            embeds.append(embed)

        view = PaginatedEmbedView(embeds)
        view.message = await ctx.send(embed=view.embeds[0], view=view)


add_md_files_as_commands(Assistance)
add_md_files_as_commands(Assistance, join(Assistance.data_dir, 'tutorial'), namespace=Assistance.tutorial)


def setup(bot):
    bot.add_cog(Assistance(bot))
