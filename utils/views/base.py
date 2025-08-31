from __future__ import annotations

from typing import Optional

import discord
from discord import Embed, Interaction, ui, ButtonStyle
from discord.ui import View, Button

from utils.utils import create_error_embed


class BasePaginator:
    """Serves as base class for paginators for a BasePaginatedView, not to be used as-is"""
    def __init__(self, n_pages: int):
        self.n_pages = n_pages
        self.idx = 0
        self.pages: dict[int, Embed] = {}

    def previous(self):
        self.idx = max(self.idx - 1, 0)

    def next(self):
        self.idx = min(self.idx + 1, self.n_pages - 1)

    def first(self):
        self.idx = 0

    def last(self):
        self.idx = self.n_pages - 1

    def is_first(self):
        return self.idx == 0

    def is_last(self):
        return self.idx == self.n_pages - 1

    def current(self):
        raise NotImplementedError


class BaseView(View):
    """Base class for all other views"""

    def __init__(self, author: 'Optional[discord.Member | discord.User]' = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message: 'Optional[discord.Message | discord.InteractionMessage]' = None
        self.author = author

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)
        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.author and interaction.user.id != self.author.id:
            await interaction.response.send_message("This view is not for you.", ephemeral=True)
            return False
        return True

    async def on_error(self, interaction: Interaction, error: Exception, item):
        embed = create_error_embed(interaction, error)
        await interaction.client.channels['bot-err'].send(embed=embed)


class BasePaginatedView(BaseView):
    """Base class for a paginated view using a BasePaginator subclass"""

    def __init__(self, paginator: BasePaginator, author: 'Optional[discord.Member | discord.User]' = None,
                 timeout: int = 30):
        super().__init__(timeout=timeout, author=author)
        self.paginator = paginator

        if self.paginator.n_pages == 1:
            self.disable_buttons()

    def reset_buttons(self):
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False

    def disable_buttons(self):
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = True
        self.last_page.disabled = True

    @discord.ui.button(label="<<", style=ButtonStyle.secondary, disabled=True)
    async def first_page(self, interaction: Interaction, button: Button):
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False
        self.paginator.first()
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label='Back', style=ButtonStyle.primary, disabled=True)
    async def prev_page(self, interaction: Interaction, button: Button):
        self.next_page.disabled = False
        self.last_page.disabled = False
        self.paginator.previous()
        if self.paginator.is_first():
            self.first_page.disabled = True
            self.prev_page.disabled = True
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label='Next', style=ButtonStyle.primary)
    async def next_page(self, interaction: Interaction, button: Button):
        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.paginator.next()
        if self.paginator.is_last():
            self.next_page.disabled = True
            self.last_page.disabled = True
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label=">>", style=ButtonStyle.secondary)
    async def last_page(self, interaction: Interaction, button: Button):
        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.next_page.disabled = True
        self.last_page.disabled = True
        self.paginator.last()
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label="Exit", style=ButtonStyle.red)
    async def remove(self, interaction: Interaction, button: Button):
        await interaction.response.edit_message(view=None)
        self.stop()


class PaginatedEmbedView(BasePaginatedView):
    def __init__(self, paginator: BasePaginator, timeout: int = 20,
                 author: 'Optional[discord.Member | discord.User]' = None):
        super().__init__(paginator=paginator, timeout=timeout, author=author)
        if self.paginator.n_pages == 1:
            self.clear_items()


class EmbedListPaginator(BasePaginator):
    def __init__(self, embeds: list[Embed]):
        super().__init__(n_pages=len(embeds))
        self.pages = {n: embed for n, embed in enumerate(embeds)}

    def current(self):
        return self.pages[self.idx]


class BaseLayoutView(ui.LayoutView):
    """Base class for all other layout views"""

    def __init__(self, author: 'Optional[discord.Member | discord.User]' = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message: 'Optional[discord.Message | discord.InteractionMessage]' = None
        self.author = author

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.delete()
        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.author and interaction.user.id != self.author.id:
            await interaction.response.send_message("This view is not for you.", ephemeral=True)
            return False
        return True

    async def on_error(self, interaction: Interaction, error: Exception, item):
        embed = create_error_embed(interaction, error)
        await interaction.client.channels['bot-err'].send(embed=embed)
