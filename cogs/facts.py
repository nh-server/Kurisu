from __future__ import annotations

import re
import secrets
from html.parser import HTMLParser
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord.ext import commands

from utils.utils import KurisuCooldown

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext


FACTS_URL = "https://facts.eiphax.tech/"
FACT_REQUEST_COUNTER_URL = (
    "https://counterapi.com/api/facts.eiphax.tech/discord-fact/request"
)


class FactsPageParser(HTMLParser):
    """Extract the visible text from each fact cell on the facts page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.facts: dict[int, str] = {}
        self._in_fact = False
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if self._in_fact:
            if tag == "br":
                self._parts.append(" ")
            return

        if tag != "td":
            return

        classes = dict(attrs).get("class", "").split()
        if "fact" in classes:
            self._in_fact = True
            self._parts = []

    def handle_endtag(self, tag):
        if not self._in_fact or tag != "td":
            return

        self._in_fact = False
        text = " ".join("".join(self._parts).split())
        match = re.match(r"(\d+)\.\s*(.*)", text, flags=re.DOTALL)
        if match:
            self.facts[int(match.group(1))] = match.group(2)

    def handle_data(self, data):
        if self._in_fact:
            self._parts.append(data)


def parse_facts(page_html: str) -> dict[int, str]:
    parser = FactsPageParser()
    parser.feed(page_html)
    parser.close()
    return parser.facts


class Facts(commands.Cog):
    """Fact lookup commands."""

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str("🔎")

    async def cog_check(self, ctx: KurisuContext) -> bool:
        if ctx.guild is None or isinstance(ctx.author, discord.User):
            return True
        return not (
            ctx.channel in self.bot.assistance_channels
            or self.bot.roles["No-Memes"] in ctx.author.roles
        )

    async def cog_command_error(self, ctx: KurisuContext, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure) and ctx.guild is not None:
            await ctx.message.delete()
            try:
                await ctx.author.send(
                    "Fact commands are disabled in this channel, or your privileges have been revoked."
                )
            except discord.Forbidden:
                await ctx.send(
                    f"{ctx.author.mention} Fact commands are disabled in this channel, "
                    "or your privileges have been revoked."
                )

    @commands.dynamic_cooldown(KurisuCooldown(1, 15.0), commands.BucketType.channel)
    @commands.command(name="fact")
    async def fact(self, ctx: KurisuContext, fact_number: str):
        """Show a numbered fact, or use "random" to show a random fact."""
        try:
            async with self.bot.session.get(FACTS_URL) as response:
                response.raise_for_status()
                facts = parse_facts(await response.text())
        except (aiohttp.ClientError, UnicodeError):
            await ctx.send("I couldn't fetch the facts page. Please try again later.")
            return

        if not facts:
            await ctx.send("I couldn't find any facts on the facts page.")
            return

        if fact_number.casefold() == "random":
            selected_number = secrets.choice(tuple(facts))
        else:
            try:
                selected_number = int(fact_number)
            except ValueError:
                await ctx.send("Use a positive fact number or `random`.")
                return

            if selected_number < 1:
                await ctx.send("Fact numbers must be positive integers.")
                return

        fact_text = facts.get(selected_number)
        if fact_text is None:
            await ctx.send(f"Fact {selected_number} was not found.")
            return

        try:
            async with self.bot.session.get(
                FACT_REQUEST_COUNTER_URL,
                params={"trackOnly": "true"},
            ) as response:
                response.raise_for_status()
                await response.read()
        except aiohttp.ClientError:
            # Counter availability should never prevent the fact from being sent.
            pass

        plain_text = discord.utils.escape_markdown(fact_text)
        source_url = f"{FACTS_URL}#{selected_number}"
        await ctx.send(
            f"{plain_text} [link](<{source_url}>)",
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def setup(bot: Kurisu):
    await bot.add_cog(Facts(bot))
