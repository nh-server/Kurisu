from __future__ import annotations

from typing import Optional

import discord
from discord import ui, ButtonStyle, Interaction, TextStyle
from discord.ui import Button, Modal, TextInput
from discord.utils import format_dt

from kurisu import Kurisu
from utils import WarnType, WarnState
from utils.database import DeletedWarnEntry, ValidWarnEntry
from utils.views.base import BaseLayoutView
from utils.warns import WARN_EXPIRATION


class WarnManagerView(BaseLayoutView):

    author: discord.Member
    warn: 'Optional[DeletedWarnEntry|ValidWarnEntry]'

    def __init__(self, bot: 'Kurisu', author: discord.Member,
                 user: discord.Member | discord.User):
        super().__init__(timeout=20, author=author)
        self.bot = bot
        self.user = user
        self.container = ui.Container()
        self.container.add_item(ui.TextDisplay(f'## {user.name} Warns\n'))
        self.container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
        self.add_item(self.container)

        self.warns = []
        self.deleted_warns = []
        self.warn_section = None
        self.warn_buttons = None

    async def init(self):
        await self.load_warns()
        self.container.add_item(WarnSelectRow(self.warns, self.deleted_warns))

    async def reload(self):
        self.container.children = self.container.children[:2]
        self.warn_section = None
        self.warn_buttons = None
        await self.init()

    async def load_warns(self):
        self.warns = [w async for w in self.bot.warns.get_warnings(self.user)]
        self.deleted_warns = [w async for w in self.bot.warns.get_deleted_warnings(self.user)]

    async def create_warn_info(self, warn: ValidWarnEntry | DeletedWarnEntry):
        issuer_user = self.bot.get_user(warn.issuer_id)
        issuer = issuer_user.mention if issuer_user else str(warn.issuer_id)
        text = (f"**ID**: {warn.warn_id}\n"
                f"**Type**: {WarnType(warn.type).name}\n"
                f"**State**: {WarnState(warn.state).name}\n"
                f"**User**: {self.user.mention}\n"
                f"**Issuer**: {issuer}\n"
                f"**Date**: {format_dt(warn.date)}\n"
                f"**Reason**: {warn.reason}\n")
        footer = ""
        title = ""
        match warn.state:
            case WarnState.Valid:
                number = await self.bot.warns.get_warning_number(warn.warn_id)
                title = f"## Warn {number}\n"
                if warn.type == WarnType.Ephemeral:
                    footer += f"-# Expires on {format_dt(warn.date + WARN_EXPIRATION)}"
                else:
                    footer += "-# This warn doesn't expire"
            case WarnState.Expired:
                title = "## Expired Warn\n"
                text += f"**Expired on**: {format_dt(warn.deletion_time)}"
            case WarnState.Deleted:
                title = "## Deleted Warn\n"
                deleter = deleter.mention if (deleter := self.bot.get_user(warn.deleter)) is not None else warn.deleter
                text += f"**Deleted on**: {format_dt(warn.deletion_time)}\n"
                text += f"**Deletion reason**: {warn.deletion_reason}\n"
                text += f"**Deleter**: {deleter}"
        return title + text + footer

    async def delete_warning(self, reason):
        await self.bot.warns.delete_warning(self.warn.warn_id, self.author.id, reason)

    async def set_warn(self, warn_id: int):
        warn = await self.bot.warns.get_warning(warn_id)

        if warn is None:
            return

        self.warn = warn

        section = ui.Section(ui.TextDisplay(await self.create_warn_info(warn)), accessory=ui.Thumbnail(media=self.user.avatar.url))
        if self.warn_section is None or self.warn_buttons is None:
            self.warn_section = section
            self.warn_buttons = WarnButtons(self)
            self.container.add_item(self.warn_section)
            self.container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
            self.container.add_item(self.warn_buttons)
        else:
            self.container.children = self.container.children[:2]
            await self.init()
            self.container.add_item(section)
            self.container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.small))
            self.container.add_item(self.warn_buttons)
            self.warn_section = section


class WarnSelectRow(ui.ActionRow[WarnManagerView]):
    def __init__(self, warns: list[ValidWarnEntry], del_warns: list[DeletedWarnEntry]):
        super().__init__()
        self.populate(warns, del_warns)

    def populate(self, warns: list[ValidWarnEntry], del_warns: list[DeletedWarnEntry]):
        for idx, warn in enumerate(warns):

            label = f"Warn {idx + 1}"
            self.select_warn.add_option(label=f"{label} {warn.date:%Y-%m-%d %H:%M:%S}", value=str(warn.warn_id),
                                        description=warn.reason[:100])
        for warn in del_warns:
            if warn.state == WarnState.Deleted:
                label = "Deleted Warn"
            else:
                label = "Expired Warn"
            self.select_warn.add_option(label=f"{label} {warn.date:%Y-%m-%d %H:%M:%S}", value=str(warn.warn_id),
                                        description=warn.reason[:100])

    @ui.select(placeholder='Select a warn')
    async def select_warn(self, interaction: discord.Interaction[Kurisu], select: discord.ui.Select) -> None:
        await self.view.set_warn(int(select.values[0]))
        await interaction.response.edit_message(view=self.view)


class WarnButtons(ui.ActionRow[WarnManagerView]):

    def __init__(self, view: WarnManagerView):
        self.__view = view
        super().__init__()
        self.update_labels()

    def update_labels(self):
        self.delete_warn.label = "Delete Warn" if self.__view.warn.state == WarnState.Valid else "Restore Warn"
        self.pin_warn.label = "Pin Warn" if self.__view.warn.type == WarnType.Ephemeral else "Unpin Warn"
        self.pin_warn.disabled = self.__view.warn.state != WarnState.Valid

    @discord.ui.button(label="Delete Warn", style=ButtonStyle.secondary)
    async def delete_warn(self, interaction: Interaction, button: Button):
        if self.__view.warn.state == WarnState.Valid:
            await interaction.response.send_modal(WarnReason(self.__view))
        else:
            await self.__view.bot.warns.restore_warning(self.__view.warn.warn_id)
            await self.__view.reload()
        await self.__view.set_warn(self.__view.warn.warn_id)
        self.update_labels()
        await interaction.response.edit_message(view=self.__view)

    @discord.ui.button(label="Pin Warn", style=ButtonStyle.secondary)
    async def pin_warn(self, interaction: Interaction, button: Button):
        if self.__view.warn.type == WarnType.Pinned:
            await self.__view.bot.warns.unpin_warning(self.__view.warn.warn_id)
        else:
            await self.__view.bot.warns.pin_warning(self.__view.warn.warn_id)
        await self.__view.set_warn(self.__view.warn.warn_id)
        self.update_labels()
        await interaction.response.edit_message(view=self.__view)


class WarnReason(Modal):
    title = "Warn Reason"
    reason = TextInput(label='Reason', style=TextStyle.short,
                       required=True, placeholder="Enter reason for warn deletion")

    def __init__(self, parent: WarnManagerView):
        super().__init__()
        self.parent = parent

    async def on_submit(self, interaction: Interaction):
        reason = self.reason.value
        if not reason:
            await interaction.response.send_message("No reason set!")
            return
        await self.parent.delete_warning(reason)
        await self.parent.set_warn(self.parent.warn.warn_id)
        await interaction.response.edit_message(view=self.parent)
