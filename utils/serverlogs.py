from datetime import datetime
from typing import Optional

import asyncpg
import discord


class ServerLogsManager:

    conn: asyncpg.Connection

    channel_blacklist = ['minecraft-console', 'dev-trusted']

    def __init__(self, bot):
        self.bot = bot

    async def init(self, url):
        try:
            self.conn = await asyncpg.connect(url)
        except:
            self.conn = None

    def build_query(
        self,
        message_content: Optional[str] = None,
        member: Optional[int] = None,
        channel: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        during: Optional[datetime] = None,
        order: str = 'DESC',
        show_mod: bool = False,
        limit: int = 100,
        sort_by_channel: bool = True,
    ) -> tuple[str, list[str | int | datetime]]:
        sql_query = (
            "SELECT gm.message_id, gm.created_at, gc.channel_id, gc.name, concat(u.name, '#',u.discriminator), gm.content FROM guild_messages gm "
            "INNER JOIN guild_channels gc ON gc.channel_id = gm.channel_id "
            "INNER JOIN users u ON u.user_id = gm.user_id  WHERE "
        )
        conditions = []
        bindings = []
        n_args = 1

        conditions.extend(f"gc.name NOT LIKE '%{c}%'" for c in self.channel_blacklist)

        if not show_mod:
            conditions.append("gc.name NOT LIKE 'mod%' and gc.name NOT LIKE 'server%'")

        if message_content:
            conditions.append(f"gm.content ~* ${n_args}")
            bindings.append(f"\\m{message_content}\\M")
            n_args = n_args + 1
        else:
            conditions.append("gm.content != ''")
        if member:
            conditions.append(f"u.user_id = ${n_args}")
            bindings.append(member)
            n_args = n_args + 1
        if channel:
            conditions.append(f"gc.channel_id = ${n_args}")
            bindings.append(channel)
            n_args = n_args + 1
        if before:
            conditions.append(f"gm.created_at < ${n_args}")
            bindings.append(before)
            n_args = n_args + 1
        if after:
            conditions.append(f"gm.created_at > ${n_args}")
            bindings.append(after)
            n_args = n_args + 1
        if during:
            conditions.append(f"gm.created_at::date = ${n_args}")
            bindings.append(during)
        sql_query += " AND ".join(conditions)
        if sort_by_channel:
            sql_query += f" ORDER BY gc.channel_id,gm.created_at {order} LIMIT {limit}"
        else:
            sql_query += f" ORDER BY gm.created_at {order} LIMIT {limit}"
        return sql_query, bindings

    async def purge_user_messages(self, user_id: int, limit: int, channel_id: int = None, before: datetime = None, after: datetime = None, during: datetime = None) -> tuple[int, list[str]]:
        deleted = 0
        failures: list[str] = []

        if self.conn is None:
            return deleted, failures

        stmt, bindings = self.build_query(member=user_id, after=after, limit=50, channel=channel_id, before=before, during=during, sort_by_channel=False)

        async with self.conn.transaction():
            async for message_id, created_at, channel_id, channel_name, _, _ in self.conn.cursor(stmt, *bindings):
                channel = self.bot.guild.get_channel(channel_id)
                if channel is None:
                    continue
                try:
                    await channel.get_partial_message(message_id).delete()
                    deleted += 1
                    if deleted == limit:
                        break
                except discord.NotFound:
                    pass
                except (discord.Forbidden, discord.HTTPException) as e:
                    status = getattr(e, "status", None)
                    code = getattr(e, "code", None)
                    failures.append(
                        f"#{channel_name}: {type(e).__name__} (status={status}, code={code})"
                    )
        return deleted, failures
