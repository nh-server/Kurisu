import asyncpg
import discord
import io

from datetime import datetime
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from kurisu import SERVER_LOGS_URL
from typing import Optional, Union
from utils.checks import is_staff_app
from utils.converters import HackIDTransformer, DateTransformer


@app_commands.guild_only
class ServerLogs(commands.GroupCog, name="serverlogs"):
    """Command group for accesing the server logs"""

    conn: asyncpg.Connection

    def __init__(self, bot):
        self.bot = bot
        self.emoji = discord.PartialEmoji.from_str('⚙')

    async def cog_load(self) -> None:
        try:
            self.conn = await asyncpg.connect(SERVER_LOGS_URL)
        except Exception as e:
            raise commands.ExtensionFailed(self.qualified_name, original=e)

    channel_blacklist = ['minecraft-console', 'dev-trusted']

    def build_query(
        self,
        message_content: Optional[str],
        member: Optional[int],
        channel: Optional[int],
        before: Optional[datetime],
        after: Optional[datetime],
        during: Optional[datetime],
        order: str,
        show_mod: bool,
        limit: int,
    ) -> tuple[str, list[Union[str, int, datetime]]]:
        sql_query = (
            "SELECT gm.created_at, gc.name, concat(u.name, '#',u.discriminator), gm.content FROM guild_messages gm "
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
        sql_query += f" ORDER BY 2,1 {order} LIMIT {limit}"
        return sql_query, bindings

    @is_staff_app("OP")
    @app_commands.describe(message_content="What to search in the message contents.",
                           member_id="ID or mention of User to search.",
                           channel_id="ID or mention of channel to search in.",
                           before="Date in yyyy-mm-dd format.",
                           after="Date in yyyy-mm-dd format.",
                           during="Date in yyyy-mm-dd format. Can't be used with before or after.",
                           order_by="Show old or new messages first. Defaults to newest messages first.",
                           show_mod_channels="If message in mod channels should be shown. Defaults to False",
                           limit="Limit of message to fetch. Max 1000. Defaults to 500.",
                           view_state="If the results file should be public or in a ephemeral message. Defaults to public")
    @app_commands.choices(
        order_by=[
            Choice(name='Older first', value='ASC',),
            Choice(name='New first', value='DESC'),
        ],
        view_state=[
            Choice(name='Public', value=""),
            Choice(name='Private', value="private")
        ]
    )
    @app_commands.command()
    async def search_messages(
            self,
            interaction: discord.Interaction,
            message_content: Optional[str] = None,
            member_id: app_commands.Transform[Optional[int], HackIDTransformer] = None,
            channel_id: app_commands.Transform[Optional[int], HackIDTransformer] = None,
            before: app_commands.Transform[Optional[datetime], DateTransformer] = None,
            after: app_commands.Transform[Optional[datetime], DateTransformer] = None,
            during: app_commands.Transform[Optional[datetime], DateTransformer] = None,
            order_by: str = "DESC",
            view_state: str = "",
            show_mod_channels: bool = False,
            limit: app_commands.Range[int, 1, 1000] = 500  # limit might change in the future but 1000 is good for now
    ):
        """Search the server logs for messages that matches the parameters given then returns them in a file"""

        await interaction.response.defer(ephemeral=bool(view_state))

        if (after or before) and during:
            return await interaction.edit_original_message(content="You can't use after or before with during.")

        stmt, bindings = self.build_query(
            message_content, member_id, channel_id, before, after, during, order_by, show_mod_channels, limit
        )

        txt = ""

        async with self.conn.transaction():
            async for created_at, channel_name, username, content in self.conn.cursor(stmt, *bindings):
                txt += f"[{channel_name}] [{created_at:%Y/%m/%d %H:%M:%S}] <{username} {content}>\n"

        if not txt:
            return await interaction.edit_original_message(content="No messages found.")

        txt_bytes = txt.encode("utf-8")

        if len(txt_bytes) > interaction.guild.filesize_limit:
            return await interaction.edit_original_message(content="Result is too big!")
        data = io.BytesIO(txt_bytes)
        file = discord.File(filename="output.txt", fp=data)
        await interaction.edit_original_message(attachments=[file])

    @is_staff_app("OP")
    @app_commands.describe(name="Name or part of the name of the channel to search",
                           view_state="If the results file should be public or in a ephemeral message. Defaults to public")
    @app_commands.choices(
        view_state=[
            Choice(name='Public', value=""),
            Choice(name='Private', value="private")
        ],
    )
    @app_commands.command()
    async def search_channels(
            self,
            interaction: discord.Interaction,
            name: str = "",
            view_state: str = "",
    ):
        """Search the server logs for channels that matches the name given then returns them in a file"""

        await interaction.response.defer(ephemeral=bool(view_state))

        query = "SELECT channel_id, name, last_updated FROM guild_channels"
        args = []

        if name:
            query += " where guild_channels.name ~* $1"
            args.append(f".*{name}.*")

        txt = ""

        async with self.conn.transaction():
            async for channel_id, name, last_updated in self.conn.cursor(query, *args):
                txt += f"{channel_id:18} | {name:50} | {last_updated:%Y/%m/%d %H:%M:%S}\n"

        if not txt:
            return await interaction.edit_original_message(content="No messages found.")

        # The padding won't be exact if the channel has unicode characters but oh well
        header = f"{'ID':18} | {'channel name':50} | {'last updated'}\n"
        txt_bytes = (header + txt).encode("utf-8")

        if len(txt_bytes) > interaction.guild.filesize_limit:
            return await interaction.edit_original_message(content="Result is too big!")
        data = io.BytesIO(txt_bytes)
        file = discord.File(filename="output.txt", fp=data)
        await interaction.edit_original_message(attachments=[file])


async def setup(bot):
    await bot.add_cog(ServerLogs(bot))
