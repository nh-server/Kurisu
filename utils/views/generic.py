from __future__ import annotations

import datetime
import discord

from discord import Interaction, ButtonStyle, ui
from discord.ui import Button
from discord.utils import format_dt, escape_markdown

from typing import TYPE_CHECKING

from utils.checks import check_staff
from utils.utils import gen_color
from utils.views.base import BaseView

if TYPE_CHECKING:
    from kurisu import Kurisu

ignored_file_extensions = (
    '.jpg',
    '.jpeg',
    'webp',
    '.gif',
    '.png',
    '.bmp',
    '.tiff',
    '.psd',
    '.sed',
)


class VoteButton(Button['SimpleVoteView']):
    label: str

    def __init__(self, custom_id: str, label: str, style: ButtonStyle = ButtonStyle.secondary):
        super().__init__(style=style, label=label, custom_id=custom_id)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        if self.view.staff_only and not check_staff(interaction.client, 'Helper', interaction.user.id):
            await interaction.response.send_message("You aren't allowed to vote.", ephemeral=True)
            return
        await interaction.client.extras.add_vote(self.view.custom_id, interaction.user.id, self.label)
        await interaction.response.send_message("Vote added.", ephemeral=True)


class VoteButtonEnd(Button['SimpleVoteView']):
    def __init__(self, custom_id: str, style: ButtonStyle = ButtonStyle.red):
        super().__init__(style=style, label='End', custom_id=custom_id)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        if interaction.user.id == self.view.author_id:
            # Try to remove the view
            await interaction.response.edit_message(view=None)

            await self.view.calculate_votes()
            results = "results:\n" + '\n'.join(f"{op}: {count}" for op, count in self.view.count.items())
            await interaction.followup.send(
                f"Vote started {format_dt(self.view.start, style='R')} has finished.\n{results}")
            self.view.stop()
            await interaction.client.extras.delete_voteview(self.view.custom_id)
        else:
            await interaction.response.send_message("Only the vote creator can end it", ephemeral=True)


class SimpleVoteView(BaseView):
    def __init__(self, bot: 'Kurisu', author_id: int, options: list[str], custom_id: int, start: datetime.datetime,
                 staff_only: bool = False):
        super().__init__(timeout=None)
        self.extras = bot.extras
        self.author_id = author_id
        self.custom_id = custom_id
        self.start = start
        self.staff_only = staff_only
        self.count: dict[str, int] = {}
        for n, option in enumerate(options):
            self.count[option] = 0
            self.add_item(VoteButton(label=option, custom_id=f"{custom_id}_{n}"))
        self.add_item(VoteButtonEnd(custom_id=f"{custom_id}_{len(self.children) + 1}"))

    async def calculate_votes(self):
        async for vote in self.extras.get_votes(self.custom_id):
            self.count[vote.option] = self.count[vote.option] + 1


class ConfirmationButtons(BaseView):
    def __init__(self, author: discord.Member | discord.User):
        super().__init__(timeout=30, author=author)
        self.value = None

    @discord.ui.button(label="Yes", style=ButtonStyle.green)
    async def confirm_button(
            self, interaction: Interaction, button: Button
    ):
        self.value = True
        # Just so the interaction doesn't fail
        await interaction.response.send_message("Confirmed", ephemeral=True)
        self.stop()

    @discord.ui.button(label="No", style=ButtonStyle.red)
    async def deny_button(
            self, interaction: Interaction, button: Button
    ):
        self.value = False
        # Just so the interaction doesn't fail
        await interaction.response.send_message("Denied", ephemeral=True)
        self.stop()


class LogLayout(ui.LayoutView):
    def __init__(self, title: str, action: str, log: str):
        super().__init__()

        container = ui.Container()
        container.accent_color = discord.Color.red()
        container.add_item(ui.TextDisplay(f"### {title}\n{action}"))
        container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
        container.add_item(ui.TextDisplay(log if log else "No content"))
        self.add_item(container)


class WatchLogLayout(ui.LayoutView):
    def __init__(self, message: discord.Message, is_edit: bool):
        super().__init__()
        assert isinstance(message.channel, discord.TextChannel)

        container = ui.Container()
        container.accent_color = gen_color(message.id)

        container.add_item(ui.TextDisplay(
            f"### {message.author.mention} posted in [{message.channel.name}]({message.jump_url}){' (edited)' if is_edit else ''}"))
        container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))

        log = escape_markdown(message.content[:2000]) if message.content else "No content"
        container.add_item(ui.TextDisplay(log))

        if message.attachments:
            text = ""
            for f in message.attachments:
                text += f"[{f.filename}]({f.url})\n"
            container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
            container.add_item(ui.TextDisplay(f"### Attachments\n{text}"))
        self.add_item(container)


class UploadLogLayout(ui.LayoutView):
    def __init__(self, message: discord.Message):
        super().__init__()
        assert isinstance(message.channel, discord.TextChannel)

        container = ui.Container()
        container.accent_color = gen_color(message.id)

        container.add_item(ui.TextDisplay(
            f"### {message.author.mention} uploaded to [{message.channel.name}]({message.jump_url})"))
        text = ""
        for f in message.attachments:
            if not f.filename.lower().endswith(ignored_file_extensions):
                text += f"[{f.filename}]({f.url}) ({f.size / 1024:0.2f} KiB)\n"
        container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
        container.add_item(ui.TextDisplay(f"{text}"))
        self.add_item(container)
