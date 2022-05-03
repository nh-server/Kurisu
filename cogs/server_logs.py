from typing import Optional

import discord
import io
import re

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from kurisu import SERVER_LOGS_URL
from sqlalchemy import create_engine, text
from utils.checks import is_staff_app


class ServerLogs(commands.GroupCog, name="serverlogs"):
    """Command group for accesing the server logs"""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = discord.PartialEmoji.from_str('⚙')
        self.engine = create_engine(SERVER_LOGS_URL) if SERVER_LOGS_URL else None

    channel_blacklist = ['minecraft-console', 'dev-trusted']

    def build_query(
            self,
            query: str,
            member: Optional[int],
            channel: Optional[int],
            before: str,
            after: str,
            during: str,
            order: str,
            show_mod: bool,
                    ):
        if query or member or channel or (during and not (before or after)) or ((before or after) and not during):
            sql_query = (
                "select gm.created_at, gc.name, concat(u.name, '#',u.discriminator), gm.content from guild_messages gm "
                "inner join guild_channels gc ON gc.channel_id =gm.channel_id "
                "inner join users u on u.user_id = gm.user_id WHERE "
            )
            conditions = []
            dict_keys = {}

            conditions.extend(f"gc.name NOT LIKE '%{c}%'" for c in self.channel_blacklist)

            if not show_mod:
                conditions.append("gc.name NOT LIKE 'mod%' and gc.name NOT LIKE 'server%'")

            if query:
                conditions.append("gm.content ~* :query")
                dict_keys["query"] = f"\\m{query}\\M"
            else:
                conditions.append("gm.content != ''")
            if member:
                conditions.append("u.user_id = :member_id")
                dict_keys["member_id"] = member
            if channel:
                conditions.append("gc.channel_id = :channel_id")
                dict_keys["channel_id"] = channel
            if before:
                if not re.match(r"20\d{2}-0[1-9]|1[0-2]-0[1-9]|[12][0-9]|3[01]", before):
                    return ""
                conditions.append("gm.created_at < :before")
                dict_keys["before"] = before
            if after:
                if not re.match(r"20\d{2}-0[1-9]|1[0-2]-0[1-9]|[12][0-9]|3[01]", after):
                    return ""
                conditions.append("gm.created_at > :after")
                dict_keys["after"] = after
            if during:
                if not re.match(r"20\d{2}-0[1-9]|1[0-2]-0[1-9]|[12][0-9]|3[01]", during):
                    return ""
                conditions.append("gm.created_at::date = :during")
                dict_keys["during"] = during

            sql_query += " AND ".join(conditions)
            sql_query += f" ORDER BY 2,1 {order}"
            stmt = text(sql_query)
            stmt = stmt.bindparams(**dict_keys)
            return stmt
        return ""

    @is_staff_app("OP")
    @app_commands.describe(query="What to search",
                           member_id_str="ID of User to search",
                           channel_id_str="ID of channel to search in.",
                           before="Date in yyyy-mm-dd format",
                           after="Date in yyyy-mm-dd format",
                           during="Date in yyyy-mm-dd format. Can't be used with before and after.",
                           order_by="Show old or new messages first.",
                           show_mod_channels="show_mod_channels")
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
    async def search(
            self,
            interaction: discord.Interaction,
            query: str = "",
            member_id_str: str = "",
            channel_id_str: str = "",
            before: str = "",
            after: str = "",
            during: str = "",
            order_by: str = "DESC",
            view_state: str = "",
            show_mod_channels: bool = False
    ):
        """Search the server logs for messages that matches the parameters given then returns them in a file"""

        if not self.engine:
            return await interaction.response.send_message("There is no database connection.", ephemeral=True)
        # Discord IDs are too long to be taken as integer input from an app command.
        try:
            member_id = None
            channel_id = None
            if member_id_str:
                member_id = int(member_id_str)
            if channel_id_str:
                channel_id = int(channel_id_str)
        except ValueError:
            interaction.response.send_message("Invalid input for IDs")
            return
        await interaction.response.defer(ephemeral=bool(view_state))
        stmt = self.build_query(
            query, member_id, channel_id, before, after, during, order_by, show_mod_channels
        )

        if not str(stmt):
            await interaction.edit_original_message(content="Invalid search.")

        with self.engine.connect() as connection:
            result = connection.execute(stmt).fetchall()
            txt = "\n".join(
                f"[{cname}] [{date.strftime('%m/%d/%Y %H:%M:%S')}] <{user} {content}>"
                for date, cname, user, content in result
            )
        if not txt:
            return await interaction.edit_original_message(content="No messages found.")
        encoded = txt.encode("utf-8")
        if len(encoded) > interaction.guild.filesize_limit:
            return await interaction.edit_original_message(content="Result is too big!")
        data = io.BytesIO(encoded)
        file = discord.File(filename="output.txt", fp=data)
        await interaction.edit_original_message(attachments=[file])


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLogs(bot))
