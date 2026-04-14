import discord
import io

from datetime import datetime
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.utils import format_dt
from typing import Optional
from utils.checks import is_staff_app
from utils.converters import HackIDTransformer, DateTransformer
from utils.utils import text_to_discord_file


@app_commands.guild_only
@app_commands.default_permissions(ban_members=True)
class ServerLogs(commands.GroupCog, name="serverlogs"):
    """Command group for accesing the server logs"""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = discord.PartialEmoji.from_str('⚙')

    @is_staff_app("OP")
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
        """Search the server logs for messages that matches the parameters given then returns them in a file

        Args:
            message_content: What to search in the message contents.
            member_id: ID or mention of User to search.
            channel_id: ID or mention of channel to search in.
            before: Date in yyyy-mm-dd format.
            after: Date in yyyy-mm-dd format.
            during: Date in yyyy-mm-dd format. Can't be used with before or after.,
            order_by: Show old or new messages first. Defaults to the newest messages first.,
            show_mod_channels: If message in mod channels should be shown. Defaults to False.
            limit: Limit of message to fetch. Max 1000. Defaults to 500.
            view_state: If the results file should be public or in a ephemeral message. Defaults to public.
            show_mod_channels: Show mod channels in results.
            limit: Maximum number of messages to show.
        """

        assert interaction.guild is not None

        await interaction.response.defer(ephemeral=bool(view_state))

        if (after or before) and during:
            return await interaction.edit_original_response(content="You can't use after or before with during.")

        stmt, bindings = self.bot.server_logs.build_query(
            message_content, member_id, channel_id, before, after, during, order_by, show_mod_channels, limit
        )

        txt = ""

        async with self.bot.server_logs.conn.transaction():
            async for _, created_at, _, channel_name, username, content in self.bot.server_logs.conn.cursor(stmt, *bindings):
                txt += f"[{channel_name}] [{created_at:%Y/%m/%d %H:%M:%S}] <{username} {content}>\n"

        if not txt:
            return await interaction.edit_original_response(content="No messages found.")

        txt_bytes = txt.encode("utf-8")

        if len(txt_bytes) > interaction.guild.filesize_limit:
            return await interaction.edit_original_response(content="Result is too big!")
        data = io.BytesIO(txt_bytes)
        file = discord.File(filename="output.txt", fp=data)
        await interaction.edit_original_response(attachments=[file])

    @is_staff_app("OP")
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
        """Search the server logs for channels that matches the name given then returns them in a file

        Args:
            name: Name or part of the name of the channel to search.
            view_state: If the results file should be public or in a ephemeral message. Defaults to public.
        """

        assert interaction.guild is not None

        await interaction.response.defer(ephemeral=bool(view_state))

        query = "SELECT channel_id, name, last_updated FROM guild_channels"
        args = []

        if name:
            query += " where guild_channels.name ~* $1"
            args.append(f".*{name}.*")

        txt = ""

        async with self.bot.server_logs.conn.transaction():
            async for channel_id, name, last_updated in self.bot.server_logs.conn.cursor(query, *args):
                txt += f"{channel_id:18} | {name:50} | {last_updated:%Y/%m/%d %H:%M:%S}\n"

        if not txt:
            return await interaction.edit_original_response(content="No messages found.")

        # The padding won't be exact if the channel has unicode characters but oh well
        header = f"{'ID':18} | {'channel name':50} | {'last updated'}\n"
        txt_bytes = (header + txt).encode("utf-8")

        if len(txt_bytes) > interaction.guild.filesize_limit:
            return await interaction.edit_original_response(content="Result is too big!")
        data = io.BytesIO(txt_bytes)
        file = discord.File(filename="output.txt", fp=data)
        await interaction.edit_original_response(attachments=[file])

    @app_commands.command()
    async def modspy(self, interaction: discord.Interaction):
        """Sends the last 20 messages in the current channel"""

        assert interaction.guild is not None
        assert interaction.channel is not None

        await interaction.response.defer(ephemeral=True)

        stmt, bindings = self.bot.server_logs.build_query(
            channel=interaction.channel.id, limit=20
        )

        stmt = f"SELECT * FROM ({stmt}) st ORDER BY 1 ASC"
        content = ""

        async with self.bot.server_logs.conn.transaction():
            async for _, created_at, _, _, username, message_content in self.bot.server_logs.conn.cursor(stmt, *bindings):
                line = f"[{format_dt(created_at)}] <{username} {message_content}>\n"
                if len(line) > 204:
                    line = f"{line[:201]}...\n"
                content += line

        if not content:
            return await interaction.edit_original_response(content="No messages found.")

        embed = discord.Embed(title=f"{interaction.channel}'s last 20 messages", description=content)
        await interaction.edit_original_response(embed=embed)

    @is_staff_app("OP")
    @app_commands.command()
    async def logsdelete(self, interaction: discord.Interaction,
                         user_id: app_commands.Transform[int, HackIDTransformer],
                         channel_id: app_commands.Transform[Optional[int], HackIDTransformer] = None,
                         before: app_commands.Transform[Optional[datetime], DateTransformer] = None,
                         after: app_commands.Transform[Optional[datetime], DateTransformer] = None,
                         during: app_commands.Transform[Optional[datetime], DateTransformer] = None,
                         limit: app_commands.Transform[int, DateTransformer] = 10,
                         ):
        """Delete messages from user according to messages stored in the server logs, deletes last limit messages by default.

            Args:
                user_id: ID or mention of User to delete messages from.
                channel_id: ID or mention of channel to delete message in.
                before: Date in yyyy-mm-dd format.
                after: Date in yyyy-mm-dd format.
                during: Date in yyyy-mm-dd format. Can't be used with before or after.
                limit: Maximum number of messages to delete.
        """

        assert interaction.guild is not None
        assert interaction.channel is not None

        await interaction.response.defer(ephemeral=True)

        if (after or before) and during:
            return await interaction.edit_original_response(content="You can't use after or before with during.")

        deleted, failures = await self.bot.server_logs.purge_user_messages(user_id, limit, channel_id, before, after, during)

        if not deleted:
            return await interaction.edit_original_response(content="No messages found for deletion!")

        files = []
        if failures:
            text = "⚠️ purge issues:\n" + "\n".join(failures)
            files.append(text_to_discord_file(text, name="Deletion failures"))

        await interaction.edit_original_response(content=f"Deleted {deleted} messages!", attachments=files)


async def setup(bot):
    await bot.add_cog(ServerLogs(bot))
