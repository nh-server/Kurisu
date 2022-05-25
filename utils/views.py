import datetime
import discord

from discord.utils import format_dt
from typing import Optional, Union
from utils import crud
from utils.checks import check_staff_id


class BasePaginator:
    """Serves as base class for paginators for a BasePaginatedView, not to be used as-is"""
    def __init__(self, n_pages):
        self.n_pages = n_pages
        self.idx = 0
        self.pages: dict[int, discord.Embed] = {}

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


class BasePaginatedView(discord.ui.View):
    """Base class for a paginated view using a BasePaginator subclass"""

    def __init__(self, paginator: BasePaginator, author: Optional[Union[discord.Member, discord.User]] = None, timeout: int = 30):
        super().__init__(timeout=timeout)
        self.paginator = paginator
        self.message: Optional[discord.Message] = None
        self.author = author

        if self.paginator.n_pages == 1:
            self.disable_buttons()

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.author and interaction.user.id != self.author.id:
            await interaction.response.send_message("This view is not for you.", ephemeral=True)
            return False
        return True

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

    @discord.ui.button(label="<<", style=discord.ButtonStyle.secondary, disabled=True)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False
        self.paginator.first()
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.primary, disabled=True)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.next_page.disabled = False
        self.last_page.disabled = False
        self.paginator.previous()
        if self.paginator.is_first():
            self.first_page.disabled = True
            self.prev_page.disabled = True
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.paginator.next()
        if self.paginator.is_last():
            self.next_page.disabled = True
            self.last_page.disabled = True
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.next_page.disabled = True
        self.last_page.disabled = True
        self.paginator.last()
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.red)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        self.stop()


class PaginatedEmbedView(BasePaginatedView):
    def __init__(self, paginator: BasePaginator, timeout: int = 20, author: Optional[Union[discord.Member, discord.User]] = None):
        super().__init__(paginator=paginator, timeout=timeout, author=author)
        if self.paginator.n_pages == 1:
            self.clear_items()


class VoteButton(discord.ui.Button['SimpleVoteView']):
    label: str

    def __init__(self, custom_id: str, label: str, style: discord.ButtonStyle = discord.ButtonStyle.secondary):
        super().__init__(style=style, label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        if self.view.staff_only and not await check_staff_id('Helper', interaction.user.id):
            await interaction.response.send_message("You aren't allowed to vote.", ephemeral=True)
            return
        await crud.add_voteview_vote(self.view.custom_id, interaction.user.id, self.label)
        await interaction.response.send_message("Vote added.", ephemeral=True)


class VoteButtonEnd(discord.ui.Button['SimpleVoteView']):
    def __init__(self, custom_id: str, style: discord.ButtonStyle = discord.ButtonStyle.red):
        super().__init__(style=style, label='End', custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        if interaction.user.id == self.view.author_id:
            # Try to remove the view
            await interaction.response.edit_message(view=None)

            await self.view.calculate_votes()
            results = "results:\n" + '\n'.join(f"{op}: {count}" for op, count in self.view.count.items())
            await interaction.followup.send(
                f"Vote started {format_dt(self.view.start, style='R')} has finished.\n{results}")
            self.view.stop()
            await crud.remove_vote_view(self.view.custom_id)
        else:
            await interaction.response.send_message("Only the vote creator can end it", ephemeral=True)


class SimpleVoteView(discord.ui.View):
    def __init__(self, author_id: int, options: list[str], custom_id: int, start: datetime.datetime, staff_only: bool = False):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.custom_id = custom_id
        self.start = start
        self.staff_only = staff_only
        self.count: dict[str, int] = {}
        for n, option in enumerate(options):
            self.count[option] = 0
            self.add_item(VoteButton(label=option, custom_id=f"{custom_id}_{n}"))
        self.add_item(VoteButtonEnd(custom_id=f"{custom_id}_{len(self.children)+1}"))

    async def calculate_votes(self):
        for vote in await crud.get_voteview_votes(self.custom_id):
            self.count[vote.option] = self.count[vote.option] + 1
