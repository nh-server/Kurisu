import asyncio
import re
import unicodedata
import json
from dataclasses import dataclass
from typing import Iterable, List, Set

import discord
from discord.ext import commands
from utils.checks import is_staff, check_staff


def normalize_text(s: str) -> str:
    return unicodedata.normalize("NFKC", s).lower()


def chunked(seq: List[str], n: int) -> Iterable[List[str]]:
    for i in range(0, len(seq), n):
        yield seq[i:i+n]


@dataclass
class Hit:
    channel_id: int
    channel_name: str
    message_id: int
    author_id: int
    author_tag: str
    created_at_iso: str
    jump_url: str
    excerpt: str


class SlurAudit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._scan_lock = asyncio.Lock()
        self._pause_event = asyncio.Event()
        self._abort_event = asyncio.Event()
        self._pause_event.set()
        self._control_channel_id: int | None = None
        self._control_guild_id: int | None = None
        self._scan_started_at: str | None = None

    async def _honor_pause_abort(self):
        if self._abort_event.is_set():
            raise RuntimeError("Scan aborted.")
        await self._pause_event.wait()
        if self._abort_event.is_set():
            raise RuntimeError("Scan aborted.")

    def _is_superop_or_owner(self, guild: discord.Guild, user_id: int) -> bool:
        try:
            if check_staff(self.bot, "SuperOP", user_id):
                return True
        except Exception:
            pass
        return bool(guild and user_id == guild.owner_id)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self._scan_lock.locked():
            return
        if message.author.bot or not message.guild:
            return
        if self._control_channel_id is None or self._control_guild_id is None:
            return
        if message.guild.id != self._control_guild_id:
            return
        if message.channel.id != self._control_channel_id:
            return
        if not self._is_superop_or_owner(message.guild, message.author.id):
            return

        content = (message.content or "").strip().lower()

        if content == ".slurprogress pause":
            self._pause_event.clear()
            await message.channel.send("Scan paused.")
            return

        if content == ".slurprogress resume":
            self._pause_event.set()
            await message.channel.send("Scan resumed.")
            return

        if content == ".slurprogress abort":
            self._abort_event.set()
            self._pause_event.set()
            await message.channel.send("Abort requested. Scan will stop shortly.")
            return

        if content == ".slursearch status":
            state = "running"
            if self._abort_event.is_set():
                state = "aborting"
            elif not self._pause_event.is_set():
                state = "paused"
            await message.channel.send(
                f"Scan status: **{state}**\n"
                f"Started: **{self._scan_started_at or 'unknown'}**"
            )
            return

    @commands.guild_only()
    @is_staff("SuperOP")
    @commands.command()
    async def slursearch(
        self,
        ctx: commands.Context,
        *,
        args: str
    ):
        kv = self._parse_kv(args)
        raw_ids = kv.get("ids")
        raw_regex = kv.get("regex")

        if not raw_ids or not raw_regex:
            await ctx.send(
                "Missing required args. Example:\n"
                '`.slursearch ids=123,456 regex="\\b(example)\\b" limit_per_channel=5000 page=500 include_threads=no delay=0.25 public_only=yes`'
            )
            return

        target_ids: Set[int] = set()
        for part in raw_ids.replace(" ", "").split(","):
            if part.isdigit():
                target_ids.add(int(part))

        if not target_ids:
            await ctx.send("No valid numeric IDs parsed from ids=...")
            return

        include_threads = kv.get("include_threads", "no").lower() in ("yes", "true", "1", "y")
        page = int(kv.get("page", "500"))
        limit_per_channel = int(kv.get("limit_per_channel", "5000"))
        delay = float(kv.get("delay", "0.25"))
        public_only = kv.get("public_only", "yes").lower() not in ("no", "false", "0", "n")

        try:
            pattern = re.compile(raw_regex, re.IGNORECASE)
        except re.error as e:
            await ctx.send(f"Regex compile error: {e}")
            return

        page = max(50, min(page, 500))
        limit_per_channel = max(100, min(limit_per_channel, 600000))
        delay = max(0.0, min(delay, 5.0))

        guild: discord.Guild = ctx.guild

        if self._scan_lock.locked():
            await ctx.send("A scan is already running. Try again later.")
            return

        self._abort_event.clear()
        self._pause_event.set()
        self._control_channel_id = ctx.channel.id
        self._control_guild_id = guild.id
        self._scan_started_at = discord.utils.utcnow().isoformat(timespec="seconds")

        try:
            async with self._scan_lock:
                await ctx.send(
                    f"Starting audit scan.\n"
                    f"- guild: **{guild.name}**\n"
                    f"- targets: **{len(target_ids)}** user IDs\n"
                    f"- regex: `{raw_regex}`\n"
                    f"- include_threads: **{include_threads}**\n"
                    f"- per-channel cap: **{limit_per_channel}** messages\n"
                    f"- page: **{page}**\n"
                    f"- delay: **{delay}** seconds\n"
                    f"- public_only: **{public_only}**\n"
                    f"- started: **{self._scan_started_at}**"
                )

                hits: List[Hit] = []
                scanned_channels = 0
                scanned_messages = 0
                skipped_channels = 0
                last_progress_report = 0

                everyone = guild.default_role
                me = guild.get_member(self.bot.user.id) or await guild.fetch_member(self.bot.user.id)

                channels_to_scan: List[discord.abc.Messageable] = []

                for ch in guild.text_channels:
                    bot_perms = ch.permissions_for(me)
                    if not (bot_perms.view_channel and bot_perms.read_message_history):
                        skipped_channels += 1
                        continue

                    if public_only:
                        pub_perms = ch.permissions_for(everyone)
                        if not pub_perms.view_channel:
                            skipped_channels += 1
                            continue

                    channels_to_scan.append(ch)

                for channel in channels_to_scan:
                    await self._honor_pause_abort()

                    scanned_channels += 1
                    channel_name = getattr(channel, "name", f"chan-{channel.id}")

                    seen = 0
                    try:
                        async for msg in channel.history(limit=limit_per_channel, oldest_first=False):
                            seen += 1
                            scanned_messages += 1

                            if scanned_messages - last_progress_report >= 5000:
                                last_progress_report = scanned_messages
                                await ctx.send(
                                    f"Progress: scanned **{scanned_channels}** channels, "
                                    f"**{scanned_messages}** messages, hits **{len(hits)}**"
                                )

                            if msg.author and msg.author.id in target_ids:
                                content = msg.content or ""
                                norm = normalize_text(content)

                                if pattern.search(norm):
                                    excerpt = content.replace("\n", " ").strip()
                                    if len(excerpt) > 180:
                                        excerpt = excerpt[:177] + "..."

                                    hits.append(
                                        Hit(
                                            channel_id=channel.id,
                                            channel_name=channel_name,
                                            message_id=msg.id,
                                            author_id=msg.author.id,
                                            author_tag=str(msg.author),
                                            created_at_iso=msg.created_at.isoformat(timespec="seconds"),
                                            jump_url=msg.jump_url,
                                            excerpt=excerpt,
                                        )
                                    )

                            if page and (seen % page == 0):
                                await self._honor_pause_abort()
                                await asyncio.sleep(delay)

                        await self._honor_pause_abort()
                        await asyncio.sleep(delay)

                    except discord.Forbidden:
                        skipped_channels += 1
                        continue
                    except json.JSONDecodeError:
                        await ctx.send("Warning: JSON decode error (likely transient HTTP issue). Retrying...")
                        await asyncio.sleep(min(5.0, max(1.0, delay)))
                        continue
                    except discord.HTTPException as e:
                        await ctx.send(f"HTTPException: {e.status}")
                        await asyncio.sleep(2.0)
                        continue

                    except Exception as e:
                        await ctx.send(f"Unexpected error: {type(e).__name__}: {e}")
                        await asyncio.sleep(2.0)
                        continue

                finished = discord.utils.utcnow().isoformat(timespec="seconds")

                if not hits:
                    await ctx.send(
                        f"Audit complete.\n"
                        f"- scanned channels: **{scanned_channels}** (skipped **{skipped_channels}**)\n"
                        f"- scanned messages: **{scanned_messages}**\n"
                        f"- hits: **0**\n"
                        f"- finished: **{finished}**"
                    )
                    return

                by_channel: dict[int, List[Hit]] = {}
                for h in hits:
                    by_channel.setdefault(h.channel_id, []).append(h)

                summary_lines = []
                for cid, hs in sorted(by_channel.items(), key=lambda x: len(x[1]), reverse=True):
                    cname = hs[0].channel_name
                    summary_lines.append(f"- #{cname}: **{len(hs)}**")

                await ctx.send(
                    f"Audit complete.\n"
                    f"- scanned channels: **{scanned_channels}** (skipped **{skipped_channels}**)\n"
                    f"- scanned messages: **{scanned_messages}**\n"
                    f"- total hits: **{len(hits)}**\n"
                    f"- finished: **{finished}**\n\n"
                    "Hits by channel:\n" + "\n".join(summary_lines[:30]) +
                    (f"\n...and {max(0, len(summary_lines)-30)} more channels." if len(summary_lines) > 30 else "")
                )

                detail_lines = []
                for h in hits:
                    detail_lines.append(
                        f"[{h.created_at_iso}] **{h.author_tag}** in **#{h.channel_name}**: {h.jump_url}\n"
                        f"> {h.excerpt}"
                    )

                for block in chunked(detail_lines, 5):
                    await self._honor_pause_abort()
                    await ctx.send("\n\n".join(block))
                    await asyncio.sleep(0.5)

        except RuntimeError as e:
            if str(e) == "Scan aborted.":
                await ctx.send("Scan aborted.")
                return
            raise

        finally:
            self._control_channel_id = None
            self._control_guild_id = None
            self._abort_event.clear()
            self._pause_event.set()
            self._scan_started_at = None

    def _parse_kv(self, s: str) -> dict:
        out = {}
        token = ""
        in_quotes = False
        quote_char = ""

        parts = []
        for ch in s:
            if ch in ("'", '"'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = ch
                    token += ch
                elif quote_char == ch:
                    in_quotes = False
                    token += ch
                else:
                    token += ch
            elif ch.isspace() and not in_quotes:
                if token:
                    parts.append(token)
                    token = ""
            else:
                token += ch
        if token:
            parts.append(token)

        for p in parts:
            if "=" not in p:
                continue
            k, v = p.split("=", 1)
            k = k.strip().lower()
            v = v.strip()
            if len(v) >= 2 and ((v[0] == v[-1]) and v[0] in ("'", '"')):
                v = v[1:-1]
            out[k] = v

        return out

    @slursearch.error
    async def slursearch_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandInvokeError) and getattr(error, "original", None):
            error = error.original

        if type(error).__name__ == "InsufficientStaffRank":
            await ctx.send(str(error))
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"Blocked: `{type(error).__name__}`")
            return

        await ctx.send(f"Error: `{type(error).__name__}: {error}`")
        raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(SlurAudit(bot))
