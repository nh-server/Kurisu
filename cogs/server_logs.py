import discord
import io
import re

from discord.ext import commands
from disnake.ext.commands import Param
from sqlalchemy import create_engine, text
from typing import Optional
from utils.checks import is_staff
from kurisu import SERVER_LOGS_URL


class ServerLogs(commands.Cog):
    """ """

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

    @commands.slash_command()
    async def serverlogs(self, inter: discord.CommandInteraction):
        pass

    @is_staff("OP")
    @commands.guild_only()
    @commands.max_concurrency(1)
    @serverlogs.sub_command()
    async def search(
            self,
            inter: discord.CommandInteraction,
            query: str = Param(default="", description="What to search"),
            member_id_str: str = Param(name="member_id", default=None, description="ID of User to search"),
            channel_id_str: str = Param(name="channel_id", default=None, description="ID of channel to search in."),
            before: str = Param(default="", description="Date in yyyy-mm-dd format"),
            after: str = Param(default="", description="Date in yyyy-mm-dd format"),
            during: str = Param(
                default="",
                description="Date in yyyy-mm-dd format. Can't be used with before and after.",
            ),
            order_by: str = Param(
                default="DESC", description="Show old or new messages first.", choices={"Older first": "ASC", "New first": "DESC"}
            ),
            view_state: str = Param(
                default="", description="If public everyone can see the output file", choices={"Public": "", "Private": "private"}
            ),
            show_mod_channels: bool = Param(default=False, description="Show mod channels"),
    ):
        """Search the server logs for messages that matches the parameters given then returns them in a file"""

        if not self.engine:
            return await inter.response.send_message("There is no database connection.", ephemeral=True)
        # Discord IDs are too long to be taken as integer input from a slash command.
        try:
            member_id = None
            channel_id = None
            if member_id_str:
                member_id = int(member_id_str)
            if channel_id_str:
                channel_id = int(channel_id_str)
        except ValueError:
            inter.response.send_message("Invalid input for ID")
            return
        await inter.response.defer(ephemeral=bool(view_state))
        stmt = self.build_query(
            query, member_id, channel_id, before, after, during, order_by, show_mod_channels
        )

        if not str(stmt):
            await inter.edit_original_message(content="Invalid search.")

        with self.engine.connect() as connection:
            result = connection.execute(stmt).fetchall()
            txt = "\n".join(
                f"[{cname}] [{date.strftime('%m/%d/%Y %H:%M:%S')}] <{user} {content}>"
                for date, cname, user, content in result
            )
        if not txt:
            return await inter.edit_original_message(content="No messages found.")
        encoded = txt.encode("utf-8")
        if len(encoded) > inter.guild.filesize_limit:
            return await inter.edit_original_message(content="Result is too big!")
        data = io.BytesIO(encoded)
        file = discord.File(filename="output.txt", fp=data)
        await inter.edit_original_message(file=file)


def setup(bot):
    bot.add_cog(ServerLogs(bot))
